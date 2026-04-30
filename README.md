# CRAVVY — D2C Snack Brand Site

Complete Flask app for the CRAVVY peanut butter slices brand. Takes mock orders, stores them in SQLite + auto-syncs to Google Sheets, has an admin dashboard.

## What's in here

- **8-section landing page** with real product photos
- **6 product detail pages** (one per SKU) with photos and big protein/fiber stamps
- **Shop page** (all 6 SKUs + 3 combo packs)
- **Cart** (server-side, persists via session)
- **Checkout** with COD/UPI/Card options
- **Order success page** with confetti
- **Admin dashboard** at `/admin`
- **Google Sheets integration** — every order auto-syncs to a Sheet for live AOV/sales tracking

## Run locally

```bash
cd cravvy-site
python -m venv venv && source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open http://localhost:5000

## Admin

Default URL: http://localhost:5000/admin
Default password: `cravvy123` — change via `ADMIN_PASSWORD` env var.

---

## ✅ Two integrations are pre-built. Configure to enable.

The code already POSTs to a Google Sheet AND sends a real customer email on every order. They just need credentials. Without env vars, they silently skip — your site still works.

---

## 🔥 Google Sheets — admin order log (5 min setup)

Every order auto-appends to a Sheet you control. Track live: order count, AOV, total sales, customer names/emails — all in one place.

### Step 1 — Create the Sheet
1. Go to [sheets.google.com](https://sheets.google.com) → **Blank**
2. Name it whatever (e.g. "CRAVVY Orders")

### Step 2 — Paste the script
1. In your Sheet: **Extensions → Apps Script**
2. Delete the boilerplate `function myFunction()` code
3. Open `google-sheets-script.js` (in this project) and copy all contents
4. Paste into Apps Script editor → **Save** (💾 icon, or Ctrl+S)

### Step 3 — Deploy as Web App
1. Click **Deploy → New deployment** (top-right)
2. Click the gear ⚙️ icon → select **Web app**
3. Configure:
   - **Description:** "CRAVVY orders endpoint"
   - **Execute as:** Me (your email)
   - **Who has access:** **Anyone** (this is critical — anonymous POSTs need to work)
4. Click **Deploy**
5. Authorize when prompted (Google → Advanced → "Go to project")
6. **Copy the Web app URL** — looks like `https://script.google.com/macros/s/AKfycb.../exec`

### Step 4 — Wire it to your app
Set the URL as an env var:

**Local:**
```bash
export GOOGLE_SHEET_WEBHOOK_URL="https://script.google.com/macros/s/.../exec"
python app.py
```

**Railway / Render:** Add `GOOGLE_SHEET_WEBHOOK_URL` to env vars → redeploy.

### Step 5 — Test it
Place a test order on your site → check the Sheet → row appears within 2-3 seconds with all order details. ✅

### What you get in the Sheet
Each row: timestamp · order # · name · email · phone · address · payment method · items ordered · item count · subtotal · shipping · total · status

Useful formulas:
- **AOV** = `=AVERAGE(O:O)` (column O = Total)
- **Total sales** = `=SUM(O:O)`
- **Orders today** = `=COUNTIF(A:A, ">="&TODAY())`
- **Top flavors** = pivot the Items column

---

## 📧 Customer email confirmations (5 min setup with Gmail)

When an order is placed, the customer receives a branded HTML email with order #, items, totals, address, and payment info. Reply-to is configurable so customer replies land in your inbox.

### Easiest option: Gmail SMTP (zero cost)

#### Step 1 — Generate a Gmail App Password
This is **not** your Gmail login password. It's a 16-char token Google issues for app SMTP access.

1. Make sure 2-Step Verification is on for your Gmail account: [myaccount.google.com/security](https://myaccount.google.com/security)
2. Go to: **[myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)**
3. Select app: "Mail" · Select device: "Other (Custom name)" → name it "CRAVVY"
4. Click **Generate**
5. **Copy the 16-character password** (no spaces — Google shows it with spaces but ignore them)

> If you don't see App Passwords, your Google account doesn't have 2FA enabled yet. Enable it first.

#### Step 2 — Set env vars

**Local:**
```bash
export SMTP_USER="orders@yourbrand.com"          # your Gmail address
export SMTP_PASS="abcdabcdabcdabcd"              # the 16-char app password
export SMTP_FROM_NAME="CRAVVY"                   # display name on the email
export SMTP_FROM_EMAIL="orders@yourbrand.com"    # usually same as SMTP_USER
export SMTP_REPLY_TO="hello@yourbrand.com"       # where customer replies go (optional)
python app.py
```

**Railway / Render:** Add the same 5 env vars in the dashboard → redeploy.

#### Step 3 — Test
Place a test order with your real email → check inbox. Should arrive within ~10 seconds.

> **Gmail SMTP limits:** ~500 emails/day, 100/hour. Plenty for early-stage launches. Switch to Resend / SendGrid / Brevo when scaling past that.

### Switching to Resend / SendGrid / Brevo
Same env vars, different SMTP_HOST/PORT:

| Provider  | SMTP_HOST              | SMTP_PORT |
|-----------|------------------------|-----------|
| Gmail     | smtp.gmail.com         | 587       |
| Resend    | smtp.resend.com        | 587       |
| SendGrid  | smtp.sendgrid.net      | 587       |
| Brevo     | smtp-relay.brevo.com   | 587       |

For Resend/SendGrid/Brevo, `SMTP_USER` is usually a fixed string like `apikey` and `SMTP_PASS` is your API key. Check their docs.

### What if SMTP fails?
The send happens on a background thread. If it fails, the order is still saved (DB + Sheet). Failures are logged — check `app.logger` output. Customer just won't get an email; admin still sees the order.

---

## Deploy

### Railway (easiest, ~3 minutes)
1. Push this folder to a GitHub repo
2. railway.app → New → Deploy from GitHub repo → pick the repo
3. Set env vars in Railway dashboard:
   - `SECRET_KEY` (random string)
   - `ADMIN_PASSWORD` (your choice)
   - `GOOGLE_SHEET_WEBHOOK_URL` (from Sheets setup above)
   - `SMTP_USER`, `SMTP_PASS`, `SMTP_FROM_EMAIL`, `SMTP_FROM_NAME`, `SMTP_REPLY_TO` (from email setup above)
4. Done — Railway gives you a `*.up.railway.app` URL

### Render (also free)
1. render.com → New → Web Service → connect repo
2. Build command: `pip install -r requirements.txt`
3. Start command: `gunicorn app:app`
4. Same env vars as Railway

### Fly.io
```bash
fly launch
fly secrets set SECRET_KEY=xxx ADMIN_PASSWORD=xxx GOOGLE_SHEET_WEBHOOK_URL=xxx SMTP_USER=xxx SMTP_PASS=xxx
fly deploy
```

## Important: SQLite & Postgres
SQLite stores orders in `cravvy.db`. On Railway/Render, this resets on dyno restart — **but** since orders also sync to Google Sheets, you have a permanent record there. SQLite is the local fast lookup; Sheets is your source of truth.

For real production with persistent local DB, switch to Postgres (Railway gives one free).

## File structure

```
cravvy-site/
├── app.py                   ← Flask app, routes, DB, Sheets webhook, email
├── products.py              ← All SKU + combo data
├── google-sheets-script.js  ← Paste this into Apps Script
├── requirements.txt
├── Procfile · runtime.txt
├── README.md                ← This file
├── cravvy.db                ← SQLite (auto-created)
├── static/
│   ├── css/style.css
│   ├── js/main.js
│   └── images/packs/        ← The 6 SKU photos
└── templates/
    ├── base.html
    ├── index.html · shop.html · product.html
    ├── cart.html · checkout.html · order_success.html
    ├── admin_login.html · admin_orders.html · 404.html
    └── email/
        ├── order_confirmation.html  ← branded HTML email
        └── order_confirmation.txt   ← plain text fallback
```

## Editing products

All product/combo/copy data lives in **`products.py`**. Edit, restart, done.

## Easter egg

Type `cravvy` anywhere on the site → confetti burst.

## What's mocked / what's real

- **Real:** cart, checkout, order persistence (SQLite + Sheets), admin dashboard, free shipping logic, **branded customer email confirmations** (when SMTP configured)
- **Mocked:** payment gateways (no real Razorpay / UPI charge yet — checkout submits a form, marks payment_method, but no charge)

## Wire up real payments later

For Razorpay (most common in India): add their JS SDK to checkout.html, create order on backend before redirect, verify signature on success. ~30 mins of work. Same for Cashfree. Stripe also works for international.

## Quick wins post-launch

1. Razorpay/Cashfree → real transactions
2. WhatsApp confirmations via Wati or AiSensy
3. Klaviyo / Brevo → abandoned-cart emails
4. `/track/<order_number>` page for delivery status
5. Inventory tracking — add stock count to PRODUCTS dict, decrement on order

