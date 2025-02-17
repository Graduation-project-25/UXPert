// const backendUrl = "http://localhost:3000"; // Localhost for development

// document.getElementById('startDetection').onclick = () => {
//     const isChecked = document.getElementById('confirmDetection').checked;
//     if (!isChecked) {
//         document.getElementById('message').innerText = 'Please confirm detection of elements.';
//         return;
//     }

//     try {
//         // Send a message to the plugin to start detection
//         parent.postMessage({ pluginMessage: { type: 'start-detection' } }, '*');
//         showMessage('Starting detection...');
//     } catch (error) {
//         console.error('Error sending message to parent:', error);
//         showMessage('Failed to start detection.');
//     } 
//     document.getElementById('message').innerText = 'Starting detection...';
// };


// async function fetchBackend() {
//     console.log("Starting fetch to backend..."); // Debug log

//     try {
//         const response = await fetch(`${backendUrl}/`, {
//             method: "GET",
//         });
//         const data = await response.text(); // Receive the response from Flask
//         figma.notify(`Backend Response: ${data}`);
//     } catch (error) {
//         figma.notify(`Error connecting to backend: ${error.message}`);
//     }
// }

