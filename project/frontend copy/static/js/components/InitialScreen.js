class InitialScreen extends HTMLElement {
    connectedCallback() {
      this.innerHTML = `
        <div id="initial-screen" style="display: none;">
          <h1>Start Detection</h1>
          <button id="start">Start</button>
        </div>
      `;
  
      this.querySelector("#start").addEventListener("click", () => {
        document.querySelector("initial-screen").style.display = "none";
        document.querySelector("processing-screen").style.display = "block";
      });
    }
  }
  
  customElements.define('initial-screen', InitialScreen);
  