let currentPageIndex = 0;
const pages = [];
let modifiedDesigns = [];
let feedbackData = {}; // Store all feedback data per frame

// Initialize UI
setTimeout(() => {
    document.getElementById('splash-screen').style.display = 'none';
    document.getElementById('initial-screen').style.display = 'block';
}, 7000);

// Start detection handler
document.getElementById('start').onclick = () => {
    document.getElementById('initial-screen').style.display = 'none';
    document.getElementById('processing-screen').style.display = 'block';

    let progress = 0;
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');

    const progressInterval = setInterval(() => {
        progress = Math.min(progress + 5, 100); // Go all the way to 100%
        progressBar.value = progress;
        progressText.textContent = `${progress}%`;
        
        if (progress === 100) {
            clearInterval(progressInterval);
            // Only request feedback after progress completes
            parent.postMessage({ pluginMessage: { type: 'start-detection' } }, '*');
        }
    }, 300);
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

    if (msg.type === 'collective-feedback') {
        document.getElementById('processing-screen').style.display = 'none';
        document.getElementById('feedback-screen').style.display = 'block';

        setTimeout(() => {
            document.getElementById('processing-screen').style.display = 'none';
            document.getElementById('feedback-screen').style.display = 'block';

            const pagesContainer = document.getElementById('pages-container');
            pagesContainer.innerHTML = '';
            pages.length = 0;
            feedbackData = {};

            msg.feedback.forEach((item, index) => {
                const frameId = item.frameId || `frame-${index}`;
                const feedbackTypes = getFeedbackTypes(item);

                // Store feedback data for navigation
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

            // Add event listeners for navigation buttons
            document.querySelectorAll('.feedback-nav-button').forEach(button => {
                button.addEventListener('click', (e) => {
                    const frameId = e.currentTarget.getAttribute('data-frame-id');
                    navigateFeedback(frameId);
                });
            });

            // Add event listeners for modify buttons
            document.querySelectorAll('.modify-button').forEach(button => {
                button.addEventListener('click', (e) => {
                    const frameId = e.currentTarget.getAttribute('data-frame-id');
                    parent.postMessage({
                        pluginMessage: {
                            type: 'request-modified-design',  // Changed from 'show-modified-design'
                            frameId: frameId
                        }
                    }, '*');
                });
            });
        }, 300);
    }
    else if (msg.type === 'design-modified') {
        // Only show modified design when we receive this message
        document.getElementById('feedback-screen').style.display = 'none';
        document.getElementById('modified-design-screen').style.display = 'block';

        document.getElementById('original-design-image').src = msg.original;
        document.getElementById('modified-design-image').src = msg.modified;

        const modList = document.getElementById('modification-list');
        modList.innerHTML = msg.modifications?.map(mod => `
            <div class="modification">
                <h4>${mod.heuristic || 'Improvement'}</h4>
                <p><strong>Element:</strong> ${mod.node_id}</p>
                <p><strong>Change:</strong> ${mod.property} → ${mod.value}</p>
                <p><strong>Reason:</strong> ${mod.reason}</p>
            </div>
        `).join('') || '<p>No modifications details available</p>';
    }
});

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
    document.getElementById('processing-screen').style.display = 'none'; 
    setTimeout(() => {
        document.getElementById('feedback-screen').style.display = 'block';
    }, 2000); 
    
    parent.postMessage({ pluginMessage: { type: 'close' } }, '*'); 
};
