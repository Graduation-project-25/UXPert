// src/main.ts
import { SplashScreen } from "./components/SplashScreen";
import { InitialScreen } from "./components/InitialScreen";
import { ProcessingScreen } from "./components/ProcessingScreen";
import { FeedbackScreen } from "./components/FeedbackScreen";

const root = document.getElementById('root');
if (!root) throw new Error("Root container not found");

// Instantiate components
const splashScreen = new SplashScreen();
const initialScreen = new InitialScreen();
const processingScreen = new ProcessingScreen();
const feedbackScreen = new FeedbackScreen();

// Append components to root
root.appendChild(splashScreen.render());
root.appendChild(initialScreen.render());
root.appendChild(processingScreen.render());
root.appendChild(feedbackScreen.render());

// Example: Show the splash screen, then initial screen
splashScreen.show();
setTimeout(() => {
  splashScreen.hide();
  initialScreen.show();
}, 2200);

// Handle "Start" button click in initial screen
initialScreen.onStart(() => {
  initialScreen.hide();
  processingScreen.show();

  // Send a message to the plugin (code.ts) to start detection
  parent.postMessage({ pluginMessage: { type: 'start-detection' } }, '*');

  // Simulate progress updates and eventually show feedback
  let progress = 0;
  const interval = setInterval(() => {
    progress += 10;
    processingScreen.updateProgress(progress);
    if (progress >= 100) {
      clearInterval(interval);
      processingScreen.hide();
      // Dummy feedback data
      const dummyFeedback = [
        {
          frameName: 'Frame 1',
          feedbackTitle: 'Consistency',
          feedbackData: { "Color": "Mismatch found", "Alignment": "Not centered" },
          screenshot: 'data:image/png;base64,...'
        }
      ];
      feedbackScreen.setFeedback(dummyFeedback);
      feedbackScreen.show();
    }
  }, 500);
});

// Listen for messages from code.ts (backend)
window.onmessage = (event) => {
  const msg = event.data.pluginMessage;
  if (msg && msg.type === 'feedback') {
    // Update the UI with feedback data received from the backend
    feedbackScreen.setFeedback(msg.data);
    feedbackScreen.show();
  }
};
