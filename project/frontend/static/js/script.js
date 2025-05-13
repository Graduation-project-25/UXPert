let currentPageIndex = 0;
const pages = [];
let modifiedDesigns = [];
let feedbackData = {};
let currentSuggestions = null;
let currentImages = null;
const ApiService = window.ApiService || (function() {
    console.error("ApiService not found!");
    return {
        getModifiedImage: () => Promise.reject("Service not available")
    };
})();

const LOADING_TYPES = {
    FEEDBACK: {
        title: "Analyzing Your Design",
        messages: [
            "Checking UX heuristics...",
            "Evaluating visual hierarchy...",
            "Identifying improvement areas..."
        ],
        tips: [
            "💡 Good UX can increase conversion rates by 400%",
            "💡 94% of first impressions are design-related"
        ]
    },
    SUGGESTIONS: {
        title: "Generating Suggestions",
        messages: [
            "Creating design improvements...",
            "Optimizing layout and spacing...",
            "Applying UX best practices..."
        ],
        tips: [
            "💡 Clear visual hierarchy improves usability by 30%",
            "💡 Well-placed CTAs can double conversions"
        ]
    },
    HISTORY: {
        title: "Loading Your History",
        messages: [
            "Retrieving your design evaluations...",
            "Gathering past feedback sessions...",
            "Preparing your history..."
        ],
        tips: [
            "Reviewing past feedback helps identify recurring issues",
            "Consistent scores indicate design maturity"
        ]
    }
};

function showLoading(type = 'FEEDBACK') {
    const config = LOADING_TYPES[type] || LOADING_TYPES.FEEDBACK;
    const screen = document.getElementById('loading-screen');
    
    const loadingContent = screen.querySelector('.loading-content');
    loadingContent.querySelector('h1').textContent = config.title;
    loadingContent.querySelector('.loading-message').textContent = 
        config.messages[Math.floor(Math.random() * config.messages.length)];
    loadingContent.querySelector('.loading-tips p').textContent = 
        config.tips[Math.floor(Math.random() * config.tips.length)];

    const progressBar = loadingContent.querySelector('.progress-fill');
    const progressText = loadingContent.querySelector('.progress-text');
    progressBar.style.width = '0%';
    progressText.textContent = '60%';
    
    screen.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function hideLoading() {
    document.getElementById('loading-screen').style.display = 'none';
    document.body.style.overflow = 'auto';
}

// Initialize UI
setTimeout(() => {
    document.getElementById('splash-screen').style.display = 'none';
    document.getElementById('initial-screen').style.display = 'block';
}, 7000);

// Start detection handler
document.getElementById('start').onclick = () => {
    document.getElementById('initial-screen').style.display = 'none';
    document.getElementById('processing-screen').style.display = 'block';

    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');
    progressBar.value = 0;
    progressText.textContent = '0%';

    parent.postMessage({ pluginMessage: { type: 'start-detection' } }, '*');

    const progressInterval = setInterval(() => {
        const currentProgress = parseInt(progressBar.value);
        if (currentProgress < 90) {
            const newProgress = Math.min(currentProgress + 5, 90);
            progressBar.value = newProgress;
            progressText.textContent = `${newProgress}%`;
        }
    }, 1000);

    const progressListener = (event) => {
        const msg = event.data.pluginMessage;
        if (msg && msg.type === 'progress-update') {
            if (msg.progress > progressBar.value) {
                progressBar.value = msg.progress;
                progressText.textContent = `${msg.progress}%`;
            }

            if (msg.progress >= 100) {
                clearInterval(progressInterval);
                window.removeEventListener('message', progressListener);
            }
        }
    };

    window.addEventListener('message', progressListener);
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
    if (feedbackTypes.length === 0) return '<div class="no-feedback">No feedback available for this category</div>';

    const currentFeedback = feedbackTypes[feedbackIndex % feedbackTypes.length];
    let html = `
        <div class="feedback-category">
            <h3 class="category-title">${currentFeedback.name}</h3>
            <div class="suggestions-list">
    `;

    if (Array.isArray(currentFeedback.data)) {
        currentFeedback.data.forEach((feedbackItem, index) => {
            const isPositive = feedbackItem.feedback?.toLowerCase().includes('good') || 
                             feedbackItem.feedback?.toLowerCase().includes('well');
            
            html += `
                <div class="suggestion-item ${isPositive ? 'positive' : ''}">
                    <h4>${feedbackItem.element_name || 'General Feedback'}</h4>
                    <p>${feedbackItem.feedback || feedbackItem}</p>
                    ${feedbackItem.score ? `<div class="score-badge">Score: ${feedbackItem.score}</div>` : ''}
                </div>
            `;
        });
    } else {
        for (const [issue, solution] of Object.entries(currentFeedback.data)) {
            html += `
                <div class="suggestion-item">
                    <h4>${issue}</h4>
                    <p>${solution}</p>
                </div>
            `;
        }
    }

    html += `</div></div>`;
    return html;
}

function navigateFeedback(frameId, direction = 1) {
    if (!feedbackData[frameId]) return;

    const feedbackTypesLength = feedbackData[frameId].feedbackTypes.length;
    feedbackData[frameId].currentFeedbackIndex = 
        (feedbackData[frameId].currentFeedbackIndex + direction + feedbackTypesLength) % feedbackTypesLength;

    const feedbackDiv = document.getElementById(`feedback-${frameId}`);
    if (feedbackDiv) {
        feedbackDiv.innerHTML = renderFeedback(
            feedbackData[frameId].item,
            feedbackData[frameId].currentFeedbackIndex
        );
    }
}

function formatHeuristicItems(text, sectionType) {
    const sectionRegex = sectionType === 'violations'
        ? /### Detected Heuristic Violations([\s\S]*?)### Suggestions to Fix/
        : /### Suggestions to Fix([\s\S]*)/;

    const sectionContent = text.match(sectionRegex)[1].trim();
    const items = sectionContent.split(/\d+\.\s+\*\*(.*?)\*\*/).slice(1);

    let html = '';
    for (let i = 0; i < items.length; i += 2) {
        const title = items[i];
        const content = items[i+1]?.trim();
        if (!title || !content) continue;
        
        html += `
            <div class="heuristic-item">
                <h3>${title}</h3>
                <ul>
                    ${content.split('-').filter(x => x.trim()).map(item => 
                        `<li>${item.trim()}</li>`
                    ).join('')}
                </ul>
            </div>
        `;
    }
    return html;
}

// Message handling
window.addEventListener('message', async (event) => {
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
                    ${feedbackTypes.length > 1 ?
                    `<button class="feedback-nav-button prev" data-frame-id="${frameId}">←</button>
                     <button class="feedback-nav-button next" data-frame-id="${frameId}">→</button>` : ''}
                    <div class="feedback-area">
                        <img src="${item.screenshot}" class="screenshot" alt="${item.frameName}">
                        <div class="feedback-content">
                            <div id="feedback-${frameId}">
                                ${renderFeedback(item)}
                            </div>
                        </div>
                    </div>
                `;
                pagesContainer.appendChild(pageSection);
                pages.push(pageSection);
            });

            showPage(0);

            // Add event listeners for navigation buttons
            document.querySelectorAll('.feedback-nav-button.prev').forEach(button => {
                button.addEventListener('click', (e) => {
                    const frameId = e.currentTarget.getAttribute('data-frame-id');
                    navigateFeedback(frameId, -1);
                });
            });

            document.querySelectorAll('.feedback-nav-button.next').forEach(button => {
                button.addEventListener('click', (e) => {
                    const frameId = e.currentTarget.getAttribute('data-frame-id');
                    navigateFeedback(frameId, 1);
                });
            });

        }, 300);

        return;
    }

    if (msg.type === 'design-modifications') {
        hideLoading();

        const suggestionsText = msg.suggestions;

        const parseSuggestions = (text) => {
            const result = {
                violations: [],
                fixes: []
            };
            
            let currentSection = null;
            let currentHeuristic = null;
            
            text.split('\n').forEach(line => {
                line = line.trim();
                
                if (line.startsWith('### Detected Heuristic Violations')) {
                    currentSection = 'violations';
                } 
                else if (line.startsWith('### Suggestions to Fix')) {
                    currentSection = 'fixes';
                }
                else if (line.match(/^\d+\.\s+\*\*(.*?)\*\*/) && currentSection) {
                    currentHeuristic = {
                        title: line.replace(/^\d+\.\s+\*\*(.*?)\*\*/, '$1').trim(),
                        points: []
                    };
                    result[currentSection].push(currentHeuristic);
                }
                else if (line.startsWith('- ') && currentSection && currentHeuristic) {
                    currentHeuristic.points.push(line.replace(/^-\s/, '').trim());
                }
            });
            
            return result;
        };

        const parsed = parseSuggestions(suggestionsText);

        const generateSectionHTML = (items, sectionTitle) => {
            if (!items || items.length === 0) return '';
            
            return `
                <div class="feedback-section">
                    <h2>${sectionTitle}</h2>
                    ${items.map(item => `
                        <div class="heuristic-item">
                            <h3>${item.title}</h3>
                            <ul>
                                ${item.points.map(point => `<li>${point}</li>`).join('')}
                            </ul>
                        </div>
                    `).join('')}
                </div>
            `;
        };

        document.getElementById('modification-summary').innerHTML = `
            <div class="feedback-container">
                ${generateSectionHTML(parsed.violations, 'Detected Heuristic Violations')}
                ${generateSectionHTML(parsed.fixes, 'Suggested Improvements')}
            </div>
        `;

        if (msg.modified_image && msg.original_image) {
            document.getElementById('design-preview').innerHTML = `
                <div class="image-comparison">
                    <div class="image-container">
                        <h4>Original Design</h4>
                        <img src="${msg.original_image}" class="design-image" />
                    </div>
                    <div class="image-container">
                        <h4>Modified Design</h4>
                        <img src="data:image/png;base64,${msg.modified_image}" class="design-image" />
                    </div>
                </div>
            `;
        }

        document.getElementById('modifications-screen').style.display = 'block';
        document.getElementById('feedback-screen').style.display = 'none';
    }

    if (msg.type === 'progress-update') {
        const progressFill = document.querySelector('.progress-fill');
        const progressText = document.querySelector('.progress-text');
        progressFill.style.width = `${msg.progress}%`;
        progressText.textContent = `${msg.progress}%`;
    }
});

// Navigation buttons
document.getElementById('prev').onclick = () => showPage(currentPageIndex - 1);
document.getElementById('next').onclick = () => showPage(currentPageIndex + 1);
document.getElementById('back').onclick = () => {
    document.getElementById('modifications-screen').style.display = 'none';
    document.getElementById('feedback-screen').style.display = 'block';
    showPage(currentPageIndex);
};

document.getElementById('modify-button').onclick = async () => {
    console.log("Modify button clicked");
    showLoading('SUGGESTIONS');
    try {
        const currentFrame = pages[currentPageIndex];
        if (!currentFrame) {
            throw new Error("No current frame found");
        }

        const frameNameElement = currentFrame.querySelector('h2');
        if (!frameNameElement) {
            throw new Error("Could not find frame name element");
        }
        
        const frameName = frameNameElement.textContent;
        console.log("Requesting modifications for frame:", frameName);
        
        parent.postMessage({
            pluginMessage: {
                type: 'request-modifications',
                frameName: frameName
            }
        }, '*');
        
    } catch (error) {
        console.error("Error in modify-button handler:", error);
        document.getElementById('error-message').textContent = `Failed to get suggestions: ${error.message}`;
        document.getElementById('error-screen').style.display = 'block';
        hideLoading();
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

document.getElementById('view-history').onclick = async () => {
    try {
        const userName = figma.currentUser?.name || "Unknown User";

        showLoading('HISTORY');
        
        const historyResponse = await ApiService.getUserHistory(userName);
        
        hideLoading();
        
        const historyList = document.getElementById('history-list');
        historyList.innerHTML = '';
        
        if (historyResponse.history && historyResponse.history.length > 0) {
            historyResponse.history.forEach(item => {
                const historyItem = document.createElement('div');
                historyItem.className = 'history-item';
                historyItem.innerHTML = `
                    <h3>${item.design_name} - ${item.frame_name}</h3>
                    <div class="meta">
                        <span>${item.date}</span>
                    </div>
                    <div class="score">Score: ${item.error_prevention_score}</div>
                `;
                historyList.appendChild(historyItem);
            });
        } else {
            historyList.innerHTML = '<div class="no-history">No history found</div>';
        }
        
        document.getElementById('feedback-screen').style.display = 'none';
        document.getElementById('history-screen').style.display = 'block';
    } catch (error) {
        console.error("Error loading history:", error);
        hideLoading();
        document.getElementById('error-message').textContent = `Failed to load history: ${error.message}`;
        document.getElementById('error-screen').style.display = 'block';
    }
};

document.getElementById('back-from-history').onclick = () => {
    document.getElementById('history-screen').style.display = 'none';
    document.getElementById('feedback-screen').style.display = 'block';
};

document.getElementById('apply-modifications').onclick = async () => {
    try {
        const modifiedImg = document.querySelector('#design-preview .image-container:nth-child(2) img');
        if (!modifiedImg?.src) throw new Error("No modified image found");
        const frameName = frameNameElement.textContent;
        parent.postMessage({
            pluginMessage: {
                type: 'apply-modifications',
                imageData: modifiedImg.src,
                frameName: frameName
            }
        }, '*');
    } catch (error) {
        figma.notify(`UI Error: ${error.message}`);
    }
};