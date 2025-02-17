// src/components/FeedbackCard.ts
export interface FeedbackCardProps {
    frameName: string;
    feedbackTitle: string;
    feedbackData: Record<string, string>;
    screenshot: string;
  }
  
  export class FeedbackCard {
    private props: FeedbackCardProps;
    private container: HTMLElement;
  
    constructor(props: FeedbackCardProps) {
      this.props = props;
      this.container = document.createElement('div');
      this.container.className = 'feedback-card';
      this.container.style.display = 'none'; // Hidden by default
  
      const image = document.createElement('img');
      image.src = this.props.screenshot;
      image.className = 'screenshot';
  
      const content = document.createElement('div');
      content.className = 'feedback-content';
      content.innerHTML = `<h2>${this.props.frameName} - ${this.props.feedbackTitle}</h2><div class='divider'></div>`;
  
      // Build the feedback list
      const ul = document.createElement('ul');
      for (const [issue, solution] of Object.entries(this.props.feedbackData)) {
        const li = document.createElement('li');
        li.innerHTML = `<strong>${issue}:</strong> ${solution}`;
        ul.appendChild(li);
      }
      content.appendChild(ul);
  
      this.container.appendChild(image);
      this.container.appendChild(content);
    }
  
    render(): HTMLElement {
      return this.container;
    }
  }
  