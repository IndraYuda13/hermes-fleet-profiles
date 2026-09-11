# Express Topup Configurator Implementation Reference

## 1. Single Reactive State Architecture

```javascript
const orderState = {
  gameId: 'mlbb',
  userId: '',
  zoneId: '',
  inquiryStatus: 'idle', // 'idle' | 'checking' | 'verified' | 'error'
  accountNickname: null,
  selectedItemId: null,
  buyerPhone: '',
  trackingToken: null,
  activeOrder: null
};
```

## 2. Race-Free Debounced Live Inquiry

```javascript
let inquiryController = null;
let debounceTimer = null;

function handleAccountInput() {
  clearTimeout(debounceTimer);
  if (inquiryController) {
    inquiryController.abort();
  }

  const { userId, zoneId, gameId } = orderState;
  if (!userId || (needsZoneId(gameId) && !zoneId)) {
    orderState.inquiryStatus = 'idle';
    orderState.accountNickname = null;
    renderInquiryBadge();
    return;
  }

  orderState.inquiryStatus = 'checking';
  renderInquiryBadge();

  debounceTimer = setTimeout(async () => {
    inquiryController = new AbortController();
    try {
      const res = await fetch(`/api/inquiry/${gameId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userId, zoneId }),
        signal: inquiryController.signal
      });
      const data = await res.json();
      if (data.success && data.nickname) {
        orderState.inquiryStatus = 'verified';
        orderState.accountNickname = data.nickname;
      } else {
        orderState.inquiryStatus = 'error';
        orderState.accountNickname = null;
      }
    } catch (err) {
      if (err.name !== 'AbortError') {
        orderState.inquiryStatus = 'error';
      }
    } finally {
      renderInquiryBadge();
    }
  }, 300);
}
```

## 3. Mobile QRIS Helper & 3-Step Guide

### 3-Step Instruction Pattern
1. **Simpan QRIS:** Tekan tombol unduh atau tangkap layar (screenshot) kode QR.
2. **Buka E-Wallet / M-Banking:** Buka BCA, GoPay, DANA, OVO, ShopeePay, atau Livin', lalu pilih opsi scan QR dari galeri foto.
3. **Konfirmasi & Bayar:** Verifikasi nominal, masukkan PIN, dan pesanan akan otomatis terproses seketika.

### Lifecycle Sync (`visibilitychange` + `focus`)
```javascript
const triggerImmediatePoll = () => {
  if (document.visibilityState === 'visible' && orderState.activeOrder?.status === 'UNPAID') {
    pollPaymentStatus(orderState.activeOrder.orderId, { immediate: true });
  }
};
document.addEventListener('visibilitychange', triggerImmediatePoll);
window.addEventListener('focus', triggerImmediatePoll);
```

## 4. Zero-DOM-Mutating SVG Registry Pattern

Avoid runtime script injection such as `lucide.createIcons()` or `data-lucide` selectors. Store vector strings in memory:

```javascript
const ICONS = {
  check: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>',
  zap: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
  arrowRight: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>'
};

function icon(name) {
  return ICONS[name] || '';
}
```

## 5. Quick Nominal Picker & Sanitized Live Feed Pattern

```javascript
// Express nominal selection directly binds to checkout state
function selectQuickNominal(product) {
  orderState.selectedItemId = product.sku;
  orderState.selectedProduct = product;
  openCheckoutDrawer();
}

// Live feed rendering with privacy masking & deterministic fallback
function renderLiveFeed(container, transactions) {
  const items = (transactions && transactions.length > 0) ? transactions : FALLBACK_FEED;
  container.innerHTML = items.map(t => `
    <div class="transaction-item">
      <div class="t-logo ${clean(t.themeClass)}">${clean(t.brandCode)}</div>
      <div class="t-name">
        <strong>${clean(t.game)} <span class="t-sku">(${clean(t.skuLabel)})</span></strong>
        <small>${rupiah(t.amount)}</small>
      </div>
      <div class="status-badge success">✔ Berhasil</div>
      <div class="t-time">${clean(t.relativeTime)}</div>
    </div>
  `).join('');
}
```
