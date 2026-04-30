"""
CRAVVY — Flask backend.

Run locally:
    pip install -r requirements.txt
    python app.py

Production: served via gunicorn (see Procfile).
"""

import os
import sqlite3
import json
import secrets
import time
import threading
import urllib.request
import urllib.error
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from datetime import datetime
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, jsonify, abort, g, flash
)

from products import (
    PRODUCTS, COMBOS, VALUE_PROPS, TESTIMONIALS,
    FREE_SHIPPING_THRESHOLD, SHIPPING_FEE,
    get_product, get_combo, all_products, all_combos
)

# ---------------------------------------------------------------------------
# App config
# ---------------------------------------------------------------------------

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

DATABASE = os.environ.get('DATABASE_PATH', os.path.join(os.path.dirname(__file__), 'cravvy.db'))
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'cravvy123')  # change in prod

# Google Sheets webhook — set via env var to enable order syncing
GOOGLE_SHEET_WEBHOOK_URL = os.environ.get('GOOGLE_SHEET_WEBHOOK_URL', '').strip()

# SMTP email config — set env vars to enable real confirmation emails
# Defaults are tuned for Gmail SMTP. Works with any SMTP server.
SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.gmail.com').strip()
SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
SMTP_USER = os.environ.get('SMTP_USER', '').strip()
SMTP_PASS = os.environ.get('SMTP_PASS', '').strip()
SMTP_FROM_EMAIL = os.environ.get('SMTP_FROM_EMAIL', SMTP_USER).strip()
SMTP_FROM_NAME = os.environ.get('SMTP_FROM_NAME', 'CRAVVY').strip()
SMTP_REPLY_TO = os.environ.get('SMTP_REPLY_TO', SMTP_FROM_EMAIL).strip()


def post_to_sheets(payload):
    """
    Fire-and-forget POST to Google Apps Script webhook.
    Runs in a background thread so order submission isn't blocked.
    Silently swallows errors so a Sheet outage never breaks checkout.
    """
    if not GOOGLE_SHEET_WEBHOOK_URL:
        return  # not configured

    def _send():
        try:
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                GOOGLE_SHEET_WEBHOOK_URL,
                data=data,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            urllib.request.urlopen(req, timeout=8)
        except Exception as e:
            # Log but don't crash — order is already saved locally
            app.logger.warning(f'Google Sheets webhook failed: {e}')

    threading.Thread(target=_send, daemon=True).start()


def send_order_email(order_data):
    """
    Fire-and-forget email send for order confirmation.
    Renders both HTML and plain-text bodies from templates.
    Silently no-ops if SMTP credentials are not configured.

    order_data: dict with keys:
        order_number, customer_name, customer_email,
        items (list of dicts), subtotal, shipping, total,
        address, city, state, pincode, payment_method
    """
    if not SMTP_USER or not SMTP_PASS:
        return  # SMTP not configured — silent skip
    if not order_data.get('customer_email'):
        return  # no recipient

    def _send():
        try:
            with app.app_context():
                html_body = render_template('email/order_confirmation.html', **order_data)
                text_body = render_template('email/order_confirmation.txt', **order_data)

            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Your CRAVVY order is in! ⚡ #{order_data['order_number']}"
            msg['From'] = formataddr((SMTP_FROM_NAME, SMTP_FROM_EMAIL))
            msg['To'] = order_data['customer_email']
            msg['Reply-To'] = SMTP_REPLY_TO
            msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))

            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(SMTP_USER, SMTP_PASS)
                server.send_message(msg)
            app.logger.info(f"Confirmation email sent: {order_data['customer_email']} / {order_data['order_number']}")
        except Exception as e:
            app.logger.warning(f"Email send failed for {order_data.get('order_number')}: {e}")

    threading.Thread(target=_send, daemon=True).start()

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """Create the orders table if it doesn't exist."""
    conn = sqlite3.connect(DATABASE)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_number TEXT UNIQUE NOT NULL,
            customer_name TEXT NOT NULL,
            customer_email TEXT NOT NULL,
            customer_phone TEXT NOT NULL,
            address TEXT NOT NULL,
            city TEXT NOT NULL,
            state TEXT NOT NULL,
            pincode TEXT NOT NULL,
            payment_method TEXT NOT NULL,
            items_json TEXT NOT NULL,
            subtotal INTEGER NOT NULL,
            shipping INTEGER NOT NULL,
            total INTEGER NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Cart helpers (session-based)
# ---------------------------------------------------------------------------

def get_cart():
    """Returns the cart from session as a list of items."""
    return session.get('cart', [])


def save_cart(cart):
    session['cart'] = cart
    session.modified = True


def cart_summary():
    """Compute totals and resolved item details."""
    cart = get_cart()
    items = []
    subtotal = 0
    total_qty = 0

    for line in cart:
        kind = line.get('kind', 'product')
        slug = line['slug']
        qty = line['qty']

        if kind == 'product':
            p = get_product(slug)
            if not p:
                continue
            line_total = p['price'] * qty
            items.append({
                'kind': 'product',
                'slug': slug,
                'name': p['name'],
                'subtitle': p['subtitle'],
                'color': p['color'],
                'on_color': p['on_color'],
                'qty': qty,
                'unit_price': p['price'],
                'line_total': line_total,
                'pack_count': qty,
            })
        else:  # combo
            c = get_combo(slug)
            if not c:
                continue
            line_total = c['price'] * qty
            items.append({
                'kind': 'combo',
                'slug': slug,
                'name': c['name'],
                'subtitle': c['tagline'],
                'color': '#FFE600',
                'on_color': '#0A0A0A',
                'qty': qty,
                'unit_price': c['price'],
                'line_total': line_total,
                'pack_count': c['qty'] * qty,
                'free_shipping': c.get('free_shipping', False),
            })

        subtotal += line_total
        total_qty += qty

    has_free_shipping_combo = any(
        i.get('kind') == 'combo' and i.get('free_shipping') for i in items
    )
    if subtotal == 0:
        shipping = 0
    elif has_free_shipping_combo or subtotal >= FREE_SHIPPING_THRESHOLD:
        shipping = 0
    else:
        shipping = SHIPPING_FEE

    return {
        'line_items': items,
        'subtotal': subtotal,
        'shipping': shipping,
        'total': subtotal + shipping,
        'total_qty': total_qty,
        'amount_to_free_shipping': max(0, FREE_SHIPPING_THRESHOLD - subtotal) if shipping > 0 else 0,
    }


@app.context_processor
def inject_cart_count():
    """Make cart count available in every template. Safe outside request context (e.g. email rendering)."""
    try:
        return {
            'cart_count': sum(line.get('qty', 0) for line in get_cart()),
        }
    except Exception:
        return {'cart_count': 0}


# ---------------------------------------------------------------------------
# Routes — pages
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    return render_template(
        'index.html',
        products=all_products(),
        combos=all_combos(),
        value_props=VALUE_PROPS,
        testimonials=TESTIMONIALS,
    )


@app.route('/shop')
def shop():
    return render_template(
        'shop.html',
        products=all_products(),
        combos=all_combos(),
    )


@app.route('/product/<slug>')
def product_detail(slug):
    p = get_product(slug)
    if not p:
        abort(404)
    others = [x for x in all_products() if x['slug'] != slug]
    return render_template('product.html', product=p, others=others[:3])


@app.route('/cart')
def cart():
    return render_template('cart.html', summary=cart_summary())


@app.route('/checkout', methods=['GET'])
def checkout():
    summary = cart_summary()
    if summary['total_qty'] == 0:
        return redirect(url_for('cart'))
    return render_template('checkout.html', summary=summary)


@app.route('/checkout', methods=['POST'])
def checkout_submit():
    summary = cart_summary()
    if summary['total_qty'] == 0:
        return redirect(url_for('cart'))

    # Collect form
    form = request.form
    required = ['name', 'email', 'phone', 'address', 'city', 'state', 'pincode', 'payment_method']
    for field in required:
        if not form.get(field, '').strip():
            flash(f"Please fill in: {field.replace('_', ' ')}", 'error')
            return render_template('checkout.html', summary=summary, form_data=form)

    # Generate order number — CRV-{ts}-{rand4}
    order_number = f"CRV-{int(time.time())}-{secrets.token_hex(2).upper()}"

    items_payload = [
        {
            'kind': i['kind'],
            'slug': i['slug'],
            'name': i['name'],
            'qty': i['qty'],
            'unit_price': i['unit_price'],
            'line_total': i['line_total'],
        }
        for i in summary['line_items']
    ]

    db = get_db()
    db.execute(
        '''INSERT INTO orders
           (order_number, customer_name, customer_email, customer_phone,
            address, city, state, pincode, payment_method,
            items_json, subtotal, shipping, total)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (
            order_number,
            form['name'].strip(),
            form['email'].strip().lower(),
            form['phone'].strip(),
            form['address'].strip(),
            form['city'].strip(),
            form['state'].strip(),
            form['pincode'].strip(),
            form['payment_method'],
            json.dumps(items_payload),
            summary['subtotal'],
            summary['shipping'],
            summary['total'],
        )
    )
    db.commit()

    # Build common order payload used by both Sheets + Email
    order_payload = {
        'order_number': order_number,
        'customer_name': form['name'].strip(),
        'customer_email': form['email'].strip().lower(),
        'customer_phone': form['phone'].strip(),
        'address': form['address'].strip(),
        'city': form['city'].strip(),
        'state': form['state'].strip(),
        'pincode': form['pincode'].strip(),
        'payment_method': form['payment_method'],
        'items': items_payload,
        'subtotal': summary['subtotal'],
        'shipping': summary['shipping'],
        'total': summary['total'],
    }

    # Fire-and-forget: send order to Google Sheet (if configured)
    items_summary = ' + '.join(f"{i['name']} x{i['qty']}" for i in items_payload)
    post_to_sheets({
        **{k: v for k, v in order_payload.items() if k != 'items'},
        'timestamp': datetime.now().isoformat() + 'Z',
        'items_summary': items_summary,
        'item_count': sum(i['qty'] for i in items_payload),
        'status': 'pending',
    })

    # Fire-and-forget: send confirmation email (if SMTP configured)
    send_order_email(order_payload)

    # Empty the cart
    session['cart'] = []
    session.modified = True

    return redirect(url_for('order_success', order_number=order_number))


@app.route('/order/<order_number>')
def order_success(order_number):
    db = get_db()
    order = db.execute(
        'SELECT * FROM orders WHERE order_number = ?', (order_number,)
    ).fetchone()
    if not order:
        abort(404)
    items = json.loads(order['items_json'])
    return render_template('order_success.html', order=order, items=items)


# ---------------------------------------------------------------------------
# Routes — cart API (JSON)
# ---------------------------------------------------------------------------

@app.route('/api/cart/add', methods=['POST'])
def api_cart_add():
    data = request.get_json(silent=True) or {}
    slug = data.get('slug')
    kind = data.get('kind', 'product')
    qty = int(data.get('qty', 1))

    if kind == 'product' and not get_product(slug):
        return jsonify({'ok': False, 'error': 'Product not found'}), 404
    if kind == 'combo' and not get_combo(slug):
        return jsonify({'ok': False, 'error': 'Combo not found'}), 404
    if qty < 1:
        return jsonify({'ok': False, 'error': 'Invalid qty'}), 400

    cart = get_cart()
    found = False
    for line in cart:
        if line['slug'] == slug and line.get('kind', 'product') == kind:
            line['qty'] += qty
            found = True
            break
    if not found:
        cart.append({'slug': slug, 'kind': kind, 'qty': qty})
    save_cart(cart)

    summary = cart_summary()
    return jsonify({
        'ok': True,
        'cart_count': summary['total_qty'],
        'subtotal': summary['subtotal'],
        'total': summary['total'],
    })


@app.route('/api/cart/update', methods=['POST'])
def api_cart_update():
    data = request.get_json(silent=True) or {}
    slug = data.get('slug')
    kind = data.get('kind', 'product')
    qty = int(data.get('qty', 0))

    cart = get_cart()
    new_cart = []
    for line in cart:
        if line['slug'] == slug and line.get('kind', 'product') == kind:
            if qty > 0:
                line['qty'] = qty
                new_cart.append(line)
            # qty 0 = drop
        else:
            new_cart.append(line)
    save_cart(new_cart)

    summary = cart_summary()
    return jsonify({
        'ok': True,
        'cart_count': summary['total_qty'],
        'subtotal': summary['subtotal'],
        'total': summary['total'],
        'shipping': summary['shipping'],
    })


@app.route('/api/cart/remove', methods=['POST'])
def api_cart_remove():
    data = request.get_json(silent=True) or {}
    slug = data.get('slug')
    kind = data.get('kind', 'product')
    cart = [l for l in get_cart() if not (l['slug'] == slug and l.get('kind', 'product') == kind)]
    save_cart(cart)
    summary = cart_summary()
    return jsonify({
        'ok': True,
        'cart_count': summary['total_qty'],
        'subtotal': summary['subtotal'],
        'total': summary['total'],
    })


@app.route('/api/cart/state')
def api_cart_state():
    summary = cart_summary()
    return jsonify(summary)


# ---------------------------------------------------------------------------
# Admin — see all mock orders
# ---------------------------------------------------------------------------

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('is_admin'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return wrapper


@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['is_admin'] = True
            return redirect(url_for('admin_orders'))
        flash('Wrong password.', 'error')
    return render_template('admin_login.html')


@app.route('/admin/orders')
@admin_required
def admin_orders():
    db = get_db()
    rows = db.execute('SELECT * FROM orders ORDER BY created_at DESC').fetchall()
    orders = []
    for r in rows:
        orders.append({
            'id': r['id'],
            'order_number': r['order_number'],
            'customer_name': r['customer_name'],
            'customer_email': r['customer_email'],
            'customer_phone': r['customer_phone'],
            'address': f"{r['address']}, {r['city']}, {r['state']} - {r['pincode']}",
            'payment_method': r['payment_method'],
            'order_items': json.loads(r['items_json']),
            'subtotal': r['subtotal'],
            'shipping': r['shipping'],
            'total': r['total'],
            'status': r['status'],
            'created_at': r['created_at'],
        })
    return render_template('admin_orders.html', orders=orders)


@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('index'))


# ---------------------------------------------------------------------------
# Misc
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.template_filter('inr')
def inr_filter(amount):
    """Format an integer as ₹X,XXX."""
    if amount is None:
        return '₹0'
    return f"₹{int(amount):,}"


# ---------------------------------------------------------------------------
# Boot
# ---------------------------------------------------------------------------

with app.app_context():
    init_db()


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_DEBUG') == '1')
