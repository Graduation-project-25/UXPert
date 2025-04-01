let currentFeedbackIndex = 0;
let feedbackCards = [];

// Splash screen disappears after 2 seconds
setTimeout(() => {
    document.getElementById('splash-screen').style.display = 'none';
    document.getElementById('initial-screen').style.display = 'block';
}, 2000);

document.getElementById('start').onclick = () => {
    document.getElementById('initial-screen').style.display = 'none';
    document.getElementById('processing-screen').style.display = 'block';
    document.getElementById('progress-container').style.display = 'block';

    let progress = 0;
    parent.postMessage({ pluginMessage: { type: 'start-detection' } }, '*');

    const progressInterval = setInterval(() => {
        progress += 5;
        document.getElementById('progress-bar').value = progress;
        document.getElementById('progress-text').innerText = `${progress}%`;

        if (progress >= 100) {
            clearInterval(progressInterval);
        }
    }, 1000);
};

document.getElementById('close').onclick = () => {
    parent.postMessage({ pluginMessage: { type: 'close' } }, '*');
};

document.getElementById('prev').onclick = () => {
    if (currentFeedbackIndex > 0) {
        showFeedbackCard(currentFeedbackIndex - 1);
    }
};

document.getElementById('next').onclick = () => {
    if (currentFeedbackIndex < feedbackCards.length - 1) {
        showFeedbackCard(currentFeedbackIndex + 1);
    }
};

document.getElementById('suggest-enhancements').onclick = () => {
    document.getElementById('feedback-screen').style.display = 'none';
    document.getElementById('enhancement-screen').style.display = 'block';
};

document.getElementById('back-to-feedback').onclick = () => {
    document.getElementById('enhancement-screen').style.display = 'none';
    document.getElementById('feedback-screen').style.display = 'block';
};

window.addEventListener("message", (event) => {
    console.log("Received plugin message:", event.data);
});



window.onmessage = (event) => {
    const msg = event.data.pluginMessage;
    if (!msg) {
        console.error("No pluginMessage found in event data:", event.data);
        return;
    }
    if (msg && msg.type === 'collective-feedback') {
        document.getElementById('processing-screen').style.display = 'none';
        document.getElementById('feedback-screen').style.display = 'block';
        document.getElementById('feedback-container').innerHTML = '';

        feedbackCards = msg.feedback.flatMap(item => {
            const cards = [];

            function createCard(title, feedbackData) {
                if (!feedbackData || Object.keys(feedbackData).length === 0) return null;

                const card = document.createElement('div');
                card.className = 'feedback-card';

                const image = document.createElement('img');
                image.src = item.screenshot;
                image.className = 'screenshot';

                let feedbackList = '<ul>';
                for (const [issue, solution] of Object.entries(feedbackData)) {
                    feedbackList += `<li><strong>${issue}:</strong> ${solution}</li>`;
                }
                feedbackList += '</ul>';

                const content = document.createElement('div');
                content.className = 'feedback-content';
                content.innerHTML = `<h2>${item.frameName} - ${title}</h2><div class='divider'></div>${feedbackList}`;

                card.appendChild(image);
                card.appendChild(content);
                document.getElementById('feedback-container').appendChild(card);

                return card;
            }

            const errorCard = createCard('Error Prevention', item.errorPreventionFeedback);
            if (errorCard) cards.push(errorCard);

            const consistencyCard = createCard('Consistency', item.consistencyFeedback);
            if (consistencyCard) cards.push(consistencyCard);

            const errHandlingCard = createCard('Error Handling', item.errorHandlingFeedback);
            if (errHandlingCard) cards.push(errHandlingCard);

            const minimalistCard = createCard('Minimalist', item.minimalistFeedback);
            if (minimalistCard) cards.push(minimalistCard);


            return cards;
        });

        showFeedbackCard(0);
    }
};

function showFeedbackCard(index) {
    feedbackCards.forEach((card, i) => {
        card.style.display = i === index ? 'flex' : 'none';
    });
    currentFeedbackIndex = index;
    document.getElementById('prev').disabled = currentFeedbackIndex === 0;
    document.getElementById('next').disabled = currentFeedbackIndex === feedbackCards.length - 1;
}

// Enable arrow key navigation
window.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowLeft') {
        document.getElementById('prev').click();
    } else if (event.key === 'ArrowRight') {
        document.getElementById('next').click();
    }
});
setTimeout(() => {
    document.getElementById('splash-screen').style.display = 'none';
    document.getElementById('initial-screen').style.display = 'block';
}, 2000);
