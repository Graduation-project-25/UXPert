
import "./components/SplashScreen.js";
import "./components/InitialScreen.js";
import "./components/ProcessingScreen.js";
import "./components/FeedbackScreen.js";
import "./components/EnhancementScreen.js";
document.addEventListener("DOMContentLoaded", () => {
  
  document.querySelector("splash-screen").style.display = "block";

 
  setTimeout(() => {
    document.querySelector("splash-screen").style.display = "none";
    document.querySelector("initial-screen").style.display = "block";
  }, 2000);
});
