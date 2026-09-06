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
