/**
 * EMS — Main JavaScript
 * Vanilla ES6+, no dependencies.
 */

'use strict';

// ── Auto-dismiss alerts after 5s ────────────
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.alert.alert-dismissible').forEach(alert => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) bsAlert.close();
    }, 5000);
  });

  // ── Confirm before POST forms with data-confirm ──
  document.querySelectorAll('form[data-confirm]').forEach(form => {
    form.addEventListener('submit', e => {
      const msg = form.dataset.confirm || 'Are you sure?';
      if (!confirm(msg)) e.preventDefault();
    });
  });

  // ── Seat progress bar live tooltip ──────────
  document.querySelectorAll('.seat-progress .progress-bar').forEach(bar => {
    const pct = bar.style.width;
    bar.setAttribute('title', `${pct} occupied`);
  });

  // ── Navbar active state from URL ────────────
  const path = window.location.pathname;
  document.querySelectorAll('.nav-link').forEach(link => {
    if (link.href && new URL(link.href).pathname === path) {
      link.classList.add('active');
    }
  });
});

// ── Utility: copy text to clipboard ─────────
function copyToClipboard(text, btn) {
  navigator.clipboard.writeText(text).then(() => {
    const orig = btn.innerHTML;
    btn.innerHTML = '<i class="bi bi-check"></i>';
    setTimeout(() => (btn.innerHTML = orig), 1800);
  });
}
