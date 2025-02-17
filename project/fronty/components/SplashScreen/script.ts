export function showSplashScreen() {
    const splashScreen = document.getElementById('splash-screen');
    splashScreen?.classList.add('show');
    setTimeout(() => {
      splashScreen?.classList.remove('show');
    }, 7000); // Remove after animation
  }
  