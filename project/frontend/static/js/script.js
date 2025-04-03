let currentPageIndex = 0;
const pages = [];
let modifiedDesigns = [];
let feedbackData = {}; 
let currentDesignState = {
    original: '',
    modified: '',
    modifications: []
};
// Store all feedback data per frame

// Initialize UI
setTimeout(() => {
    document.getElementById('splash-screen').style.display = 'none';
    document.getElementById('initial-screen').style.display = 'block';
}, 7000);

// Start detection handler
document.getElementById('start').onclick = () => {
    document.getElementById('initial-screen').style.display = 'none';
    document.getElementById('processing-screen').style.display = 'block';

    // Start progress animation
    let progress = 0;
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');

    const progressInterval = setInterval(() => {
        progress = Math.min(progress + 5, 90);
        progressBar.value = progress;
        progressText.textContent = `${progress}%`;
    }, 300);

    parent.postMessage({ pluginMessage: { type: 'start-detection' } }, '*');
};

// Navigation functions
function showPage(index) {
    pages.forEach((page, i) => {
        page.style.display = i === index ? 'block' : 'none';
    });
    currentPageIndex = index;
    document.getElementById('prev').disabled = currentPageIndex === 0;
    document.getElementById('next').disabled = currentPageIndex === pages.length - 1;
}

function getFeedbackTypes(item) {
    console.log("item.recognitionFeedback");
    console.log(item.recognitionFeedback);
    return [
        { name: 'Error Prevention', data: item.errorPreventionFeedback, type: 'errorPreventionFeedback' },
        { name: 'Consistency and Standards', data: item.consistencyFeedback, type: 'consistencyFeedback' },
        { name: 'Help Users Recognize, Diagnose, and Recover from Errors', data: item.errorHandlingFeedback, type: 'errorHandlingFeedback' },
        { name: 'Aesthetic and Minimalist Design', data: item.minimalistFeedback, type: 'minimalistFeedback' },
        { name: 'Recognition Rather than Recall', data: item.recognitionFeedback, type: 'recognitionFeedback' }
    ].filter(f => f.data && Object.keys(f.data).length > 0);
}

function renderFeedback(item, feedbackIndex = 0) {
    const feedbackTypes = getFeedbackTypes(item);
    if (feedbackTypes.length === 0) return '<p>No feedback available</p>';

    const currentFeedback = feedbackTypes[feedbackIndex % feedbackTypes.length];
    let html = `<h3>${currentFeedback.name} </h3><div class='divider'></div><ul>`;

    // Handle both recognition and minimalist feedback as arrays
    if (['Recognition Rather than Recall', 'Aesthetic and Minimalist Design'].includes(currentFeedback.name) && Array.isArray(currentFeedback.data)) {
        currentFeedback.data.forEach(feedbackItem => {
            if (typeof feedbackItem === 'string') {
                // If feedbackItem is a string, display it directly
                html += `<li>${feedbackItem}</li>`;
            } else {
                // Use specific keys for minimalist feedback
                const issueLabel = feedbackItem.issue === "White Space Ratio" ? "White Space Ratio" :
                                  feedbackItem.issue === "Number of Elements" ? "Number of Elements" :
                                  feedbackItem.issue === "Irrelevant Elements" ? "Irrelevant Elements" :
                                  feedbackItem.issue === "Score" ? "Score" :
                                  feedbackItem.element_name || 'Issue';
                html += `
                    <li>
                        <strong>${issueLabel}:</strong> ${feedbackItem.feedback}
                    </li>
                `;
            }
        });
    } else {
        // Handle object feedback (e.g., errorPreventionFeedback, consistencyFeedback)
        for (const [issue, solution] of Object.entries(currentFeedback.data)) {
            html += `<li><strong>${issue}:</strong> ${solution}</li>`;
        }
    }

    html += '</ul>';
    return html;
}

function navigateFeedback(frameId) {
    if (!feedbackData[frameId]) return;

    feedbackData[frameId].currentFeedbackIndex =
        (feedbackData[frameId].currentFeedbackIndex + 1) % feedbackData[frameId].feedbackTypes.length;

    const feedbackDiv = document.getElementById(`feedback-${frameId}`);
    if (feedbackDiv) {
        feedbackDiv.innerHTML = renderFeedback(
            feedbackData[frameId].item,
            feedbackData[frameId].currentFeedbackIndex
        );
    }
}

// Message handling
window.addEventListener('message', (event) => {
    const msg = event.data.pluginMessage;
    if (!msg) return;

    // Hide all screens first
    document.querySelectorAll('.screen').forEach(el => {
        el.style.display = 'none';
    });

    switch (msg.type) {
        case 'processing-started':
            document.getElementById('processing-screen').style.display = 'block';
            break;

        case 'collective-feedback':
            handleFeedbackScreen(msg);
            break;

        case 'design-modified':
            currentDesignState = {
                original: msg.original,
                modified: msg.modified,
                modifications: msg.modifications || []
            };
            showModifiedDesignScreen();
            break;

        case 'modification-error':
            showErrorScreen(msg);
            break;

        case 'processing-finished':
            // No need to handle separately as other screens will show
            break;
    }
});

function handleFeedbackScreen(msg) {
    // Complete progress bar
    document.getElementById('progress-bar').value = 100;
    document.getElementById('progress-text').textContent = '100%';

    const pagesContainer = document.getElementById('pages-container');
    pagesContainer.innerHTML = '';
    pages.length = 0;
    feedbackData = {};

    msg.feedback.forEach((item, index) => {
        const frameId = item.frameId || `frame-${index}`;
        const feedbackTypes = getFeedbackTypes(item);

        feedbackData[frameId] = {
            item,
            feedbackTypes,
            currentFeedbackIndex: 0
        };

        const pageSection = document.createElement('div');
        pageSection.className = 'page-section';
        pageSection.style.display = index === 0 ? 'block' : 'none';
        pageSection.innerHTML = `
            <h2>${item.frameName}</h2>
            <div class="feedback-area">
                <img src="${item.screenshot}" class="screenshot" alt="${item.frameName}">
                <div class="feedback-content">
                    <div id="feedback-${frameId}">
                        ${renderFeedback(item)}
                    </div>
                    ${feedbackTypes.length > 1 ?
                    `<button class="feedback-nav-button" data-frame-id="${frameId}">→</button>` : ''}
                </div>
            </div>
            <button class="modify-button" data-frame-id="${frameId}">Show Modified Design</button>
        `;
        pagesContainer.appendChild(pageSection);
        pages.push(pageSection);
    });

    showPage(0);
    document.getElementById('feedback-screen').style.display = 'block';

    // Add event listeners
    document.querySelectorAll('.feedback-nav-button').forEach(button => {
        button.addEventListener('click', (e) => {
            const frameId = e.currentTarget.getAttribute('data-frame-id');
            navigateFeedback(frameId);
        });
    });

    document.querySelectorAll('.modify-button').forEach(button => {
        button.addEventListener('click', (e) => {
            const frameId = e.currentTarget.getAttribute('data-frame-id');
            parent.postMessage({
                pluginMessage: {
                    type: 'request-modified-design',
                    frameId: frameId
                }
            }, '*');
        });
    });
}

function showModifiedDesignScreen() {
    document.getElementById('original-design-image').src = currentDesignState.original;
    document.getElementById('modified-design-image').src = currentDesignState.modified;
    
    const modList = document.getElementById('modification-list');
    modList.innerHTML = currentDesignState.modifications.length > 0
        ? currentDesignState.modifications.map(mod => `
            <li class="modification-item">
                <strong>${mod.heuristic || 'Improvement'}:</strong>
                <p>${mod.reason || 'No reason provided'}</p>
                <small>${mod.node_id} • ${mod.property} → ${mod.value}</small>
            </li>
        `).join('')
        : '<li>No modifications suggested</li>';
    
    document.getElementById('modified-design-screen').style.display = 'block';
}

function showErrorScreen(msg) {
    document.getElementById('error-message').textContent = msg.error;
    if (msg.original) {
        document.getElementById('original-design-image').src = msg.original;
    }
    document.getElementById('error-screen').style.display = 'block';
}

// Update your navigation functions
document.getElementById('back-to-feedback-from-mod').onclick = () => {
    document.getElementById('modified-design-screen').style.display = 'none';
    document.getElementById('feedback-screen').style.display = 'block';
    showPage(currentPageIndex);
};
// Navigation buttons
document.getElementById('prev').onclick = () => showPage(currentPageIndex - 1);
document.getElementById('next').onclick = () => showPage(currentPageIndex + 1);

// Screen transitions
document.getElementById('suggest-enhancements').onclick = () => {
    document.getElementById('feedback-screen').style.display = 'none';
    document.getElementById('enhancement-screen').style.display = 'block';
};

document.getElementById('back-to-feedback').onclick = () => {
    document.getElementById('enhancement-screen').style.display = 'none';
    document.getElementById('feedback-screen').style.display = 'block';
    showPage(currentPageIndex);
};

document.getElementById('back-to-feedback-from-mod').onclick = () => {
    document.getElementById('modified-design-screen').style.display = 'none';
    document.getElementById('feedback-screen').style.display = 'block';
    showPage(currentPageIndex);
};

document.getElementById('close').onclick = () => {
    parent.postMessage({ pluginMessage: { type: 'close' } }, '*');
};