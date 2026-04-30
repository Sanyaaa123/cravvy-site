// =====================================================================
// CRAVVY frontend JS — cart interactivity, toasts, steppers, FX
// =====================================================================

(function () {
  'use strict';

  // -------------------------------------------------------------------
  // Toast
  // -------------------------------------------------------------------
  function showToast(message, ms = 2200) {
    let toast = document.querySelector('.toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.className = 'toast';
      document.body.appendChild(toast);
    }
    toast.textContent = message;
    requestAnimationFrame(() => toast.classList.add('show'));
    clearTimeout(toast._t);
    toast._t = setTimeout(() => toast.classList.remove('show'), ms);
  }

  // -------------------------------------------------------------------
  // Cart — server-side via JSON API
  // -------------------------------------------------------------------
  async function cartAdd(slug, kind = 'product', qty = 1) {
    try {
      const res = await fetch('/api/cart/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ slug, kind, qty }),
      });
      const data = await res.json();
      if (!data.ok) {
        showToast('Couldn\'t add to cart');
        return;
      }
      updateCartCount(data.cart_count);
      showToast(`Added! ${data.cart_count} pack${data.cart_count !== 1 ? 's' : ''} in cart ⚡`);
      burstConfetti();
    } catch (e) {
      showToast('Network error');
    }
  }

  async function cartUpdate(slug, kind, qty) {
    const res = await fetch('/api/cart/update', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ slug, kind, qty }),
    });
    return res.json();
  }

  async function cartRemove(slug, kind) {
    const res = await fetch('/api/cart/remove', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ slug, kind }),
    });
    return res.json();
  }

  function updateCartCount(n) {
    document.querySelectorAll('[data-cart-count]').forEach(el => {
      el.textContent = n;
    });
  }

  // -------------------------------------------------------------------
  // Confetti — yellow lightning burst on cart-add
  // -------------------------------------------------------------------
  function burstConfetti() {
    const burst = document.createElement('div');
    burst.style.cssText = `
      position: fixed; top: 50%; left: 50%; pointer-events: none;
      transform: translate(-50%, -50%); z-index: 8000;
    `;
    for (let i = 0; i < 18; i++) {
      const bolt = document.createElement('div');
      const angle = (i / 18) * 360;
      const distance = 80 + Math.random() * 80;
      const colors = ['#FFE600', '#FF6A1A', '#EC2C8A', '#7B3FF2', '#00A19A', '#B8DC2A'];
      bolt.textContent = '⚡';
      bolt.style.cssText = `
        position: absolute; left: 0; top: 0;
        font-size: ${16 + Math.random() * 18}px;
        color: ${colors[i % colors.length]};
        transform: translate(0, 0) rotate(${Math.random() * 360}deg);
        transition: transform 0.7s cubic-bezier(.3,1,.5,1), opacity 0.7s;
      `;
      burst.appendChild(bolt);
      requestAnimationFrame(() => {
        const x = Math.cos(angle * Math.PI / 180) * distance;
        const y = Math.sin(angle * Math.PI / 180) * distance;
        bolt.style.transform = `translate(${x}px, ${y}px) rotate(${360 + Math.random() * 360}deg) scale(0.4)`;
        bolt.style.opacity = '0';
      });
    }
    document.body.appendChild(burst);
    setTimeout(() => burst.remove(), 800);
  }

  // -------------------------------------------------------------------
  // Bind add-to-cart buttons
  // -------------------------------------------------------------------
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-add-to-cart]');
    if (btn) {
      e.preventDefault();
      e.stopPropagation();   // make sure parent <a> doesn't navigate
      const slug = btn.dataset.slug;
      const kind = btn.dataset.kind || 'product';
      // Look for a qty input in the same buy-row context
      const ctx = btn.closest('.product-buy-row, .flavor-buy, .product-info, .shop-card, .combo-card');
      const qtyInput = ctx ? ctx.querySelector('[data-qty-input]') : null;
      const qty = qtyInput ? Math.max(1, parseInt(qtyInput.value || '1', 10)) : 1;
      cartAdd(slug, kind, qty);
    }
  });

  // -------------------------------------------------------------------
  // Quantity steppers (product page, etc.)
  // -------------------------------------------------------------------
  document.addEventListener('click', (e) => {
    const inc = e.target.closest('[data-qty-inc]');
    const dec = e.target.closest('[data-qty-dec]');
    if (inc || dec) {
      e.preventDefault();
      const stepper = (inc || dec).closest('.qty-stepper');
      const input = stepper.querySelector('input');
      let v = parseInt(input.value, 10) || 1;
      if (inc) v = Math.min(99, v + 1);
      else v = Math.max(1, v - 1);
      input.value = v;
      input.dispatchEvent(new Event('change'));
    }
  });

  // -------------------------------------------------------------------
  // Cart page — line item updates
  // -------------------------------------------------------------------
  async function refreshCartPage() {
    // simplest: reload to keep totals + shipping meter in sync
    window.location.reload();
  }

  document.addEventListener('click', async (e) => {
    const removeBtn = e.target.closest('[data-cart-remove]');
    if (removeBtn) {
      e.preventDefault();
      const slug = removeBtn.dataset.slug;
      const kind = removeBtn.dataset.kind || 'product';
      const data = await cartRemove(slug, kind);
      if (data.ok) {
        updateCartCount(data.cart_count);
        refreshCartPage();
      }
    }
    const cartInc = e.target.closest('[data-cart-inc]');
    const cartDec = e.target.closest('[data-cart-dec]');
    if (cartInc || cartDec) {
      e.preventDefault();
      const btn = cartInc || cartDec;
      const slug = btn.dataset.slug;
      const kind = btn.dataset.kind || 'product';
      const currentQty = parseInt(btn.dataset.qty, 10);
      const newQty = cartInc ? currentQty + 1 : currentQty - 1;
      const data = await cartUpdate(slug, kind, newQty);
      if (data.ok) {
        updateCartCount(data.cart_count);
        refreshCartPage();
      }
    }
  });

  // -------------------------------------------------------------------
  // Pack-stage cursor parallax (hero)
  // -------------------------------------------------------------------
  const packs = document.querySelectorAll('.pack-stage .pack');
  if (packs.length && window.matchMedia('(min-width: 901px)').matches) {
    let rafId = null;
    document.addEventListener('mousemove', (e) => {
      if (rafId) return;
      rafId = requestAnimationFrame(() => {
        const x = (e.clientX / window.innerWidth - 0.5) * 2;
        const y = (e.clientY / window.innerHeight - 0.5) * 2;
        packs.forEach((pack, i) => {
          const intensity = (i % 2 === 0 ? 1 : -1) * 6;
          pack.style.translate = `${x * intensity}px ${y * intensity}px`;
        });
        rafId = null;
      });
    });
  }

  // -------------------------------------------------------------------
  // Easter egg: type 'cravvy' anywhere
  // -------------------------------------------------------------------
  let buffer = '';
  document.addEventListener('keydown', (e) => {
    if (e.target.matches('input, textarea')) return;
    buffer += e.key.toLowerCase();
    if (buffer.length > 6) buffer = buffer.slice(-6);
    if (buffer === 'cravvy') {
      buffer = '';
      for (let i = 0; i < 5; i++) setTimeout(burstConfetti, i * 100);
      showToast('you found it ⚡', 3000);
    }
  });

  // -------------------------------------------------------------------
  // Auto-flash dismiss
  // -------------------------------------------------------------------
  document.querySelectorAll('.flash').forEach((f) => {
    setTimeout(() => f.style.opacity = '0', 4000);
    setTimeout(() => f.remove(), 4400);
  });

  // -------------------------------------------------------------------
  // Payment option click → check radio
  // -------------------------------------------------------------------
  document.querySelectorAll('.payment-option').forEach(opt => {
    opt.addEventListener('click', () => {
      const radio = opt.querySelector('input[type="radio"]');
      if (radio) radio.checked = true;
      document.querySelectorAll('.payment-option').forEach(o => o.classList.remove('checked'));
      opt.classList.add('checked');
    });
  });
  // Initial state
  document.querySelectorAll('.payment-option input[type="radio"]:checked').forEach(r => {
    r.closest('.payment-option')?.classList.add('checked');
  });
})();
