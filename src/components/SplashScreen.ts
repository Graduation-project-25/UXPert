// src/components/SplashScreen.ts
import { BaseComponent } from "./BaseComponent";

export class SplashScreen implements BaseComponent {
  private container: HTMLElement;

  constructor() {
    this.container = document.createElement('div');
    this.container.id = 'splash-screen';
    this.container.innerHTML = `
      <h1>
        <span class="letter">U</span>
        <span class="letter">X</span>
        <span class="letter">P</span>
        <span class="letter">e</span>
        <span class="letter">r</span>
        <span class="letter">t</span>
      </h1>
    `;
  }

  render(): HTMLElement {
    return this.container;
  }

  show(): void {
    this.container.style.display = 'flex';
    // Example: Hide splash screen after 2 seconds
    setTimeout(() => {
      this.hide();
    }, 2000);
  }

  hide(): void {
    this.container.style.display = 'none';
  }
}
