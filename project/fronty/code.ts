import { showSplashScreen } from './components/SplashScreen/script';
import { initInitialScreen } from './components/InitialScreen/script';
import { showProcessingScreen, updateProgress } from './components/ProcessingScreen/script';
import { renderFeedback } from './components/FeedbackScreen/script';

// Initialize the app
function initApp() {
  showSplashScreen();
  initInitialScreen();
  showProcessingScreen();
//   renderFeedback();
}

// Start the app
initApp();
