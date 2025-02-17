class FeedbackScreen extends HTMLElement {
    connectedCallback() {
      this.innerHTML = `
        <div id="feedback-screen" style="display: none;">
          <h1>Feedback</h1>
          <div id="feedback-container"></div>
          <div id="nav-buttons">
            <button id="prev" disabled>Previous</button>
            <button id="next" disabled>Next</button>
          </div>
          <button id="close">Close</button>
          <button id="suggest-enhancements" class="button">Suggest Enhancements</button>
        </div>
      `;
  
      this.querySelector("#suggest-enhancements").addEventListener("click", () => {
        document.querySelector("feedback-screen").style.display = "none";
        document.querySelector("enhancement-screen").style.display = "block";
      });
  
      this.querySelector("#close").addEventListener("click", () => {
        document.querySelector("feedback-screen").style.display = "none";
        document.querySelector("initial-screen").style.display = "block";
      });
    }
  }
  
  customElements.define('feedback-screen', FeedbackScreen);
  