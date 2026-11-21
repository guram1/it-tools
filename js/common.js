// Toast notification
function showToast(msg = 'Copied to clipboard!') {
    const t = document.getElementById('toast');
    if (!t) return;
    t.textContent = msg;
    t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 2000);
}

// Copy to clipboard
function copyToClipboard(id) {
    const el = document.getElementById(id);
    if (!el) return;
    navigator.clipboard.writeText(el.textContent).then(() => showToast());
}

// Range slider sync
function initRangeSliders() {
    document.querySelectorAll('.range-input[data-display]').forEach(input => {
        const display = document.getElementById(input.dataset.display);
        if (display) {
            input.addEventListener('input', () => display.textContent = input.value);
        }
    });
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', initRangeSliders);

// Shareable tool state: read/write simple key=value pairs in the URL query string.
// Usage: const p = getToolParams(); ... setToolParams({ip: '10.0.0.0', cidr: 24});
function getToolParams() {
    const out = {};
    new URLSearchParams(location.search).forEach((v, k) => { out[k] = v; });
    return out;
}
function setToolParams(obj) {
    const u = new URL(location.href);
    Object.keys(obj).forEach(k => {
        const v = obj[k];
        if (v === undefined || v === null || v === '') u.searchParams.delete(k); else u.searchParams.set(k, v);
    });
    history.replaceState(null, '', u.pathname + (u.searchParams.toString() ? '?' + u.searchParams.toString() : '') + u.hash);
}
function copyShareLink() {
    navigator.clipboard.writeText(location.href).then(() => showToast('Link copied!'));
}
// Debounce helper for live (as-you-type) results.
function debounce(fn, ms = 250) {
    let t; return function (...a) { clearTimeout(t); t = setTimeout(() => fn.apply(this, a), ms); };
}
