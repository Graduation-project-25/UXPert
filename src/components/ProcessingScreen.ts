// src/components/ProcessingScreen.ts
import { BaseComponent } from "./BaseComponent";

export class ProcessingScreen implements BaseComponent {
  private container: HTMLElement;
  private progressBar: HTMLProgressElement;
  private progressText: HTMLElement;

  constructor() {
    this.container = document.createElement('div');
    this.container.id = 'processing-screen';
    this.container.style.display = 'none';

    const header = document.createElement('h1');
    header.textContent = 'Processing...';

    const infoText = document.createElement('p');
    infoText.textContent = 'Please wait while the design is being evaluated.';

    const progressContainer = document.createElement('div');
    progressContainer.id = 'progress-container';

    this.progressBar = document.createElement('progress');
    this.progressBar.id = 'progress-bar';
    this.progressBar.max = 100;
    this.progressBar.value = 0;

    this.progressText = document.createElement('p');
    this.progressText.id = 'progress-text';
    this.progressText.textContent = '0%';

    progressContainer.appendChild(this.progressBar);
    progressContainer.appendChild(this.progressText);

    this.container.appendChild(header);
    this.container.appendChild(infoText);
    this.container.appendChild(progressContainer);
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

  updateProgress(value: number): void {
    this.progressBar.value = value;
    this.progressText.textContent = `${value}%`;
  }
}
