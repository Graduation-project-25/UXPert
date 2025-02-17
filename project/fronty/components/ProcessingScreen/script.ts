export function showProcessingScreen() {
    const processingScreen = document.getElementById('processing-screen');
    processingScreen?.classList.add('show');
  }
  
  export function updateProgress(progress: number) {
    const progressBar = document.getElementById('progress-bar') as HTMLProgressElement;
    if (progressBar) {
      progressBar.value = progress;
    }
  }
  