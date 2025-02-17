export function renderFeedback(feedback: any) {
    const feedbackContainer = document.getElementById('feedback-container');
    feedback.forEach((item) => {
      const card = document.createElement('div');
      card.classList.add('feedback-card');
      
      card.innerHTML = `
        <div class="screenshot">
          <img src="${item.screenshot}" alt="screenshot"/>
        </div>
        <div class="feedback-content">
          <ul>
            ${Object.entries(item.consistencyFeedback).map(([key, value]) => `<li>${key}: ${value}</li>`).join('')}
          </ul>
        </div>
      `;
      feedbackContainer?.appendChild(card);
      card.style.display = 'flex'; // Make it visible
    });
  }
  