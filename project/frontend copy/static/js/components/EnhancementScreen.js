class EnhancementScreen extends HTMLElement {
    connectedCallback() {
      this.innerHTML = `
        <div id="enhancement-screen" style="display: none;">
          <h1>Suggestions</h1>
          <p>Here are specific actions you can take to improve your heuristic rules, enhance design consistency, and usability:</p>
          <ul>
            <li><strong>Adopt a Consistent Color Palette:</strong> Use a uniform color scheme.</li>
            <li><strong>Align Elements for Better Visual Hierarchy:</strong> Maintain proper alignment.</li>
            <li><strong>Adjust Sizes for Proportional Relationships:</strong> Keep sizes consistent.</li>
            <li><strong>Incorporate Whitespace Effectively:</strong> Ensure enough spacing.</li>
            <li><strong>Ensure Accessibility Compliance:</strong> Use contrast checkers.</li>
          </ul>
          <button id="back-to-feedback" class="suggestion-button">Back to Feedback</button>
        </div>
      `;
  
      this.querySelector("#back-to-feedback").addEventListener("click", () => {
        document.querySelector("enhancement-screen").style.display = "none";
        document.querySelector("feedback-screen").style.display = "block";
      });
    }
  }
  
  customElements.define('enhancement-screen', EnhancementScreen);
  