class ProcessingScreen extends HTMLElement {
    connectedCallback() {
      this.innerHTML = `
        <div id="processing-screen" style="display: none;">
          <h1>Processing...</h1>
          <p>Please wait while the design is being evaluated.</p>
          <div id="progress-container">
            <progress id="progress-bar" max="100" value="0"></progress>
            <p id="progress-text">0%</p>
          </div>
        </div>
      `;
  
      // Simulate progress
      let progress = 0;
      const progressBar = this.querySelector("#progress-bar");
      const progressText = this.querySelector("#progress-text");
  
      const interval = setInterval(() => {
        if (progress < 100) {
          progress += 10;
          progressBar.value = progress;
          progressText.textContent = `${progress}%`;
        } else {
          clearInterval(interval);
          document.querySelector("processing-screen").style.display = "none";
          document.querySelector("feedback-screen").style.display = "block";
        }
      }, 500);
    }
  }
  
  customElements.define('processing-screen', ProcessingScreen);
  