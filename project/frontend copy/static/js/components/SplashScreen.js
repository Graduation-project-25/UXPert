class SplashScreen extends HTMLElement {
    connectedCallback() {
      this.innerHTML = `
        <div id="splash-screen">
          <h1>
            <span class="letter">U</span>
            <span class="letter">X</span>
            <span class="letter">P</span>
            <span class="letter">e</span>
            <span class="letter">r</span>
            <span class="letter">t</span>
          </h1>
        </div>
      `;
    }
  }
  
  customElements.define('splash-screen', SplashScreen);
  