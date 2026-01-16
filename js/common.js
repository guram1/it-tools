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
