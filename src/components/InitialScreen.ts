// src/components/InitialScreen.ts
import { BaseComponent } from "./BaseComponent";

export class InitialScreen implements BaseComponent {
  private container: HTMLElement;
  private startButton: HTMLButtonElement;

  constructor() {
    this.container = document.createElement('div');
    this.container.id = 'initial-screen';
    this.container.style.display = 'none';
    
    // Create a header and a start button
    const header = document.createElement('h1');
    header.textContent = 'Start Detection';
    
    this.startButton = document.createElement('button');
    this.startButton.id = 'start';
    this.startButton.textContent = 'Start';

    // Append elements
    this.container.appendChild(header);
    this.container.appendChild(this.startButton);
  }

  render(): HTMLElement {
    return this.container;
  }

  show(): void {
    this.container.style.display = 'flex';
  }

  hide(): void {
    this.container.style.display = 'none';
  }

  // Attach event handler
  onStart(callback: () => void) {
    this.startButton.addEventListener('click', callback);
  }
}
