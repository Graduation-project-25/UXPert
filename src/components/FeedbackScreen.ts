// src/components/FeedbackScreen.ts
import { BaseComponent } from "./BaseComponent";
import { FeedbackCard, FeedbackCardProps } from "./FeedbackCard";

export class FeedbackScreen implements BaseComponent {
  private container: HTMLElement;
  private feedbackContainer: HTMLElement;
  private feedbackCards: FeedbackCard[] = [];
  private currentIndex = 0;

  constructor() {
    this.container = document.createElement('div');
    this.container.id = 'feedback-screen';
    this.container.style.display = 'none';

    const header = document.createElement('h1');
    header.textContent = 'Feedback';

    this.feedbackContainer = document.createElement('div');
    this.feedbackContainer.id = 'feedback-container';

    // Navigation buttons
    const navButtons = document.createElement('div');
    navButtons.id = 'nav-buttons';

    const prevButton = document.createElement('button');
    prevButton.id = 'prev';
    prevButton.textContent = 'Previous';
    prevButton.disabled = true;

    const nextButton = document.createElement('button');
    nextButton.id = 'next';
    nextButton.textContent = 'Next';
    nextButton.disabled = true;

    navButtons.appendChild(prevButton);
    navButtons.appendChild(nextButton);

    this.container.appendChild(header);
    this.container.appendChild(this.feedbackContainer);
    this.container.appendChild(navButtons);

    // Example event listeners for navigation (you might want to expose these to the outside as well)
    prevButton.addEventListener('click', () => this.showFeedbackCard(this.currentIndex - 1));
    nextButton.addEventListener('click', () => this.showFeedbackCard(this.currentIndex + 1));
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

  // Populate feedback cards using provided data
  setFeedback(feedbackData: FeedbackCardProps[]) {
    // Clear current cards
    this.feedbackCards = [];
    this.feedbackContainer.innerHTML = '';

    // Create new cards
    feedbackData.forEach(data => {
      const card = new FeedbackCard(data);
      this.feedbackCards.push(card);
      this.feedbackContainer.appendChild(card.render());
    });
    // Show the first card if available
    if (this.feedbackCards.length > 0) {
      this.showFeedbackCard(0);
    }
  }

  showFeedbackCard(index: number) {
    if (index < 0 || index >= this.feedbackCards.length) return;

    // Hide all cards and show only the selected one
    this.feedbackCards.forEach((card, i) => {
      card.render().style.display = (i === index) ? 'flex' : 'none';
    });
    this.currentIndex = index;
    // Optionally, update navigation button states here
  }
}
