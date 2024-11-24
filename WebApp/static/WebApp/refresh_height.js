function refreshBackgroundHeight() {
    const background = document.querySelector('.bg');
    const contentHeight = document.body.scrollHeight; // Total height of the content
    background.style.height = `${contentHeight}px`;
}

// Refresh height on page load
window.onload = refreshBackgroundHeight;