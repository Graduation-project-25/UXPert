// script.js
document.getElementById('startDetection').onclick = () => {
    const isChecked = document.getElementById('confirmDetection').checked;
    if (!isChecked) {
        document.getElementById('message').innerText = 'Please confirm detection of elements.';
        return;
    }

    // Send a message to the plugin to start detection
    parent.postMessage({ pluginMessage: { type: 'start-detection' } }, '*');
    document.getElementById('message').innerText = 'Starting detection...';
};
