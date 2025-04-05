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
        
        if (progress === 50) {
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
function showModifications(data) {
    const modList = document.getElementById('modification-list');
    modList.innerHTML = '';
    
    if (data.modifications && data.modifications.length > 0) {
        data.modifications.forEach(mod => {
            const item = document.createElement('div');
            item.className = 'modification-item';
            item.innerHTML = `
                <h4>${mod.element_name || mod.element_id || 'Element'}</h4>
                ${mod.issues ? mod.issues.map(issue => `
                    <div class="issue">
                        <p><strong>Heuristic:</strong> ${issue.heuristic}</p>
                        <p><strong>Problem:</strong> ${issue.problem}</p>
                        <p><strong>Solution:</strong> ${issue.solution}</p>
                        <p><strong>Priority:</strong> ${issue.priority}</p>
                    </div>
                `).join('') : ''}
            `;
            modList.appendChild(item);
        });
    } else {
        modList.innerHTML = '<p>No modifications suggested for this frame</p>';
    }
    
    document.getElementById('feedback-screen').style.display = 'none';
    document.getElementById('modifications-screen').style.display = 'block';
}

function showLoading() {
    document.getElementById('processing-screen').style.display = 'block';
}

function hideLoading() {
    document.getElementById('processing-screen').style.display = 'none';
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
            document.querySelectorAll('modify-button-query').forEach(button => {
                button.addEventListener('click', (e) => {
                    const frameId = e.currentTarget.getAttribute('data-frame-id');
                    console.log('Requesting modifications for frame:', frameId);
                    
                    // Show loading state
                    document.getElementById('processing-screen').style.display = 'block';
                    
                    parent.postMessage({
                        pluginMessage: {
                            type: 'request-modifications',
                            frameId: frameId
                        }
                    }, '*');
                }
            );
            }
        );
        }, 300);
    
    return;
}


if (msg.type === 'design-modifications') {
    hideLoading();
    console.log('Received modifications:', msg);
    
    if (msg.modifications && msg.modifications.length > 0) {
        showModifications(msg);
    } else {
        showError('No modifications suggested for this frame');
    }
    return;
}
if (msg.type === 'progress-update') {
    document.getElementById('progress-bar').value = msg.progress;
    document.getElementById('progress-text').textContent = `${msg.progress}%`;
    return;
}

});
// Navigation buttons
document.getElementById('prev').onclick = () => showPage(currentPageIndex - 1);
document.getElementById('next').onclick = () => showPage(currentPageIndex + 1);



document.getElementById('modify-button').onclick = async () => {
    showLoading();
    
    try {
        const currentFrame = pages[currentPageIndex];
        const frameName = currentFrame.querySelector('h2')?.textContent;
        
        const response = await new Promise((resolve, reject) => {
            parent.postMessage({
                pluginMessage: {
                    type: 'request-modifications',
                    frameName: frameName
                }
            }, '*');
                 setTimeout(() => reject(new Error("Request timeout")), 30000);
        });
        
    } catch (error) {
        console.error("Modification error:", error);
        showError(`Failed to get modifications: ${error.message}`);
    }
};

document.getElementById('back-to-feedback-from-mods').onclick = () => {
    document.getElementById('modifications-screen').style.display = 'none';
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
