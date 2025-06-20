let currentPageIndex = 0;
const pages = [];
let modifiedDesigns = [];
let feedbackData = {};
let currentSuggestions = null;
let currentImages = null; // Store all feedback data per frame

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
console.log("Script loaded - checking for history button");

// Ensure we only add the listener once
if (!window.historyButtonInitialized) {
    document.getElementById('view-history-btn')?.addEventListener('click', function() {
        const frameId = this.closest('#modifications-screen').dataset.frameId;
        
        if (!frameId) {
            console.error("No frame ID in DOM");
            alert("Please generate suggestions first");
            return;
        }

        parent.postMessage({
            pluginMessage: {
                type: 'request-suggestions-history',
                frameId: frameId
            }
        }, '*');
    });
    
    window.historyButtonInitialized = true;
}
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
    document.getElementById('page-back').disabled = currentPageIndex === 0;
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

// Navigation function for feedback
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
// Show suggestions history
function showSuggestionsHistory(frameId) {
    const historyContainer = document.getElementById('history-container');
    historyContainer.innerHTML = `
        <div class="loading-state">
            <div class="loader"></div>
            <p>Loading suggestions history...</p>
        </div>
    `;
    
    // Use classList instead of style.display
    document.getElementById('history-view').classList.remove('hidden');
    document.getElementById('modifications-screen').classList.add('hidden');
    
    parent.postMessage({
        pluginMessage: {
            type: 'request-suggestions-history',
            frameId: frameId
        }
    }, '*');
}

// Display history items
function displayHistory(historyItems, frameId) {
    console.log("Displaying history:", historyItems); // Debug log
    
    const historyContainer = document.getElementById('history-container');
    const historyView = document.getElementById('history-view');
    const modificationsScreen = document.getElementById('modifications-screen');
    
    // Ensure elements exist
    if (!historyContainer || !historyView || !modificationsScreen) {
        console.error("Critical elements missing in DOM");
        return;
    }

    // Clear previous content
    historyContainer.innerHTML = '';
    
    if (!historyItems || historyItems.length === 0) {
        historyContainer.innerHTML = `
            <div class="no-history-message">
                <img src="https://cdn-icons-png.flaticon.com/512/4076/4076478.png" width="64">
                <h3>No Suggestions History Found</h3>
                <p>We couldn't find any previous suggestions for this design.</p>
                <p>Modify the design to generate new suggestions.</p>
            </div>
        `;
    } else {
        historyItems.forEach((item, index) => {
            const historyItem = document.createElement('div');
            historyItem.className = 'history-item';
            historyItem.innerHTML = `
                <div class="history-header">
                    <h3>Version ${index + 1}</h3>
                    <small>${new Date(item.timestamp).toLocaleString()}</small>
                </div>
                <div class="history-suggestions">${item.text}</div>
                <img src="data:image/png;base64,${item.image_data}" class="history-image" />
                <button class="view-version" data-frame-id="${frameId}" data-version-id="${index}">
                    View This Version
                </button>
            `;
            historyContainer.appendChild(historyItem);
        });
    }
    
    // Update visibility
    modificationsScreen.classList.add('hidden');
    historyView.classList.remove('hidden');
    
    console.log("History view should now be visible"); // Debug log
}


function renderFeedbackObject(feedbackObj) {
    if (!feedbackObj || typeof feedbackObj !== 'object') return 'None';
    return Object.entries(feedbackObj).map(
        ([key, value]) => `<p><strong>${key}:</strong> ${value}</p>`
    ).join('');
}

// Click handler for version restoration
document.addEventListener('click', function(event) {
    // Get the clicked element with safety checks
    var target = event.target;
    while (target && target.nodeName !== 'BUTTON' && target !== document) {
        target = target.parentNode;
    }
    
    // Check if it's a version button
    if (target && target.classList && target.classList.contains('view-version')) {
        const frameId = target.getAttribute('data-frame-id');
        const versionId = target.getAttribute('data-version-id');
        
        // Validate before sending
        if (frameId && versionId) {
            figma.ui.postMessage({
                type: 'restore-version',
                frameId: frameId,
                versionId: parseInt(versionId, 10)  // Convert to number
            });
        }
    }
});
// Ensure script runs after DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM fully loaded, initializing UI handlers"); // Debug log

    // Verify view-history button exists
    const viewHistoryButton = document.getElementById('view-history');
    if (viewHistoryButton) {
        console.log("View History button found, attaching event listener"); // Debug log
        viewHistoryButton.onclick = async () => {
            console.log("View History button clicked"); // Debug log
            alert("View History button clicked!"); // Visual confirmation
            try {
                showLoading('HISTORY');
                console.log("Sending request-history message"); // Debug log
                parent.postMessage({
                    pluginMessage: {
                        type: 'request-history'
                    }
                }, '*');
            } catch (error) {
                console.error("Error in view-history handler:", error); // Debug log
                hideLoading();
                document.getElementById('error-message').textContent = `Failed to load history: ${error.message}`;
                document.getElementById('error-screen').style.display = 'block';
            }
        };
    } else {
        console.error("View History button not found in DOM"); // Debug log
        alert("Error: View History button not found!");
    }
});

// Message handling
window.addEventListener('message', async (event) => {
    console.log("Received message in UI:", event.data); // Debug log
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
                <div class="feedback-area">
                    <div class="nav-buttons">
                        ${feedbackTypes.length > 1 ? `
                            <button class="feedback-nav-button prev" data-frame-id="${frameId}">←</button>
                            <button class="feedback-nav-button next" data-frame-id="${frameId}">→</button>
                        ` : ''}
                    </div>
                    <div class="content-wrapper">
                        <img src="${item.screenshot}" class="screenshot" alt="${item.frameName}">
                        <div class="feedback-content">
                            <div id="feedback-${frameId}">
                                ${renderFeedback(item)}
                            </div>
                        </div>
                    </div>
                </div>
            `;
            pagesContainer.appendChild(pageSection);
            pages.push(pageSection);
        });

        // Add the "Suggestions Preview" button at the end of pagesContainer
        // const modifyButtonContainer = document.createElement('div');
        // modifyButtonContainer.style.display = 'flex';
        // modifyButtonContainer.style.justifyContent = 'center';
        // modifyButtonContainer.style.marginTop = '30px';
        // modifyButtonContainer.style.marginBottom = '20px';

        // const modifyButton = document.createElement('button');
        // modifyButton.id = 'modify-button';
        // modifyButton.className = 'mod_button';
        // modifyButton.textContent = 'Suggestions Preview';

        // modifyButtonContainer.appendChild(modifyButton);
        // pagesContainer.appendChild(modifyButtonContainer);
        // modifyButton.addEventListener('click', () => {
         
        // });

        showPage(0);

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

        const modScreen = document.getElementById('modifications-screen');
        modScreen.dataset.frameId = msg.frameId

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
    console.log("Attempting to attach history button listener");
    const historyBtn = document.getElementById('view-history-btn');
    console.log("Found button element:", historyBtn);

    
    if (msg?.type === 'suggestions-history-data') {
        console.log("Received history data:", {
            frameId: msg.frameId,
            count: msg.history?.length || 0
        });
        displayHistory(msg.history, msg.frameId);
    }
    else if (msg?.type === 'history-error') {
        console.error("History error:", msg.message);
        const historyContainer = document.getElementById('history-container');
        if (historyContainer) {
            historyContainer.innerHTML = `
                <div class="error-message">
                    <h3>Error Loading History</h3>
                    <p>${msg.message || 'Could not load suggestions history'}</p>
                    <button onclick="showSuggestionsHistory('${msg.frameId}')">
                        Try Again
                    </button>
                </div>
            `;
        }
    }

    if (msg.type === 'history-data') {
    hideLoading();
    const historyList = document.getElementById('history-list');
    historyList.innerHTML = '';

    if (msg.history && msg.history.length > 0) {
       msg.history.forEach(item => {
    const historyItem = document.createElement('div');
    historyItem.className = 'history-item';

    const ep = item.error_prevention_results || {};
    const cons = item.consistency_results || {};
    const eh = item.error_handling_results || {};
    const min = item.minimalist_results?.Feedback || [];
    const recog = item.recognition_results || [];

    const formatted = `
        <h3>${item.design_name} - ${item.frame_name}</h3>
        <div class="meta"><span>${item.date}</span></div>

        <div class="section error-prevention">
            <h4>Error Prevention</h4>
           
            <div><strong>Feedback:</strong>
                ${renderFeedbackObject(ep.Feedback)}
            </div>
        </div>

        <div class="section consistency">
            <h4>Consistency</h4>

            <div><strong>Feedback:</strong>
                ${renderFeedbackObject(cons.Feedback)}
            </div>
        </div>

        <div class="section error-handling">
            <h4>Error Handling</h4>
            <p><strong>Score:</strong> ${eh.ErrorHandlingScore ?? 'N/A'}</p>
            <p><strong>Recovery Issues:</strong> ${eh.RecoveryIssues?.join(', ') || 'None'}</p>
            <div><strong>Feedback:</strong>
                ${renderFeedbackObject(cons.Feedback)}
            </div>
        </div>

        <div class="section minimalist">
            <h4>Minimalist</h4>
            ${min.map(f => `
                <div class="minimal-item">
                    <p><strong>Issue:</strong> ${f.issue}</p>
                    <div></div>
                   <div><strong>Feedback:</strong>
                ${renderFeedbackObject(cons.Feedback)}
            </div>
                </div>
            `).join('')}
        </div>

        <div class="section recognition">
            <h4>Recognition</h4>
            ${recog.map(f => `
                <div class="recognition-item">
                    <p><strong>Element:</strong> ${f.element_name}</p>
                    <p><strong>Type:</strong> ${f.element_type}</p>
                    <div><strong>Feedback:</strong>
                        ${renderFeedbackObject(cons.Feedback)}
                    </div>
                </div>
            `).join('')}
        </div>
    `;

    historyItem.innerHTML = formatted;
    historyList.appendChild(historyItem);
});


    } else {
        historyList.innerHTML = '<div class="no-history-message"><h3>No history found</h3></div>';
    }

    document.getElementById('feedback-screen').style.display = 'none';
    document.getElementById('history-screen').style.display = 'block';
}


    if (msg.type === 'history-error') {
        console.error("Received history-error:", msg); // Debug log
        alert("History error: " + msg.message); // Visual confirmation
        hideLoading();
        document.getElementById('error-message').textContent = `Failed to load history: ${msg.message}`;
        document.getElementById('error-screen').style.display = 'block';
    }
});

// Navigation buttons
document.getElementById('page-back').onclick = () => showPage(currentPageIndex - 1);
document.getElementById('next').onclick = () => showPage(currentPageIndex + 1);

document.getElementById('modify-button').onclick = async () => {
    console.log("Modify button clicked");
    showLoading('SUGGESTIONS');
    try {
        const currentFrame = pages[currentPageIndex];
        if (!currentFrame) throw new Error("No current frame found");
        
        const frameNameElement = currentFrame.querySelector('h2');
        if (!frameNameElement) throw new Error("Could not find frame name element");
        
        const frameName = frameNameElement.textContent;
        const screenshot = currentFrame.querySelector('.screenshot').src;
        
        console.log("Requesting modifications with current screenshot");
        
        parent.postMessage({
            pluginMessage: {
                type: 'request-modifications',
                frameName: frameName,
                currentImage: screenshot, // Pass current image data
                forceRefresh: true       // Force new generation
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
document.getElementById('back-to-feedback-from-history').onclick = () => {
    document.getElementById('history-screen').style.display = 'none';
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

document.getElementById('view-history-btn')?.addEventListener('click', function() {
    const frameId = this.closest('#modifications-screen').dataset.frameId;
    
    if (!frameId) {
        console.error("No frame ID in DOM");
        alert("Please generate suggestions first");
        return;
    }

    parent.postMessage({
        pluginMessage: {
            type: 'request-suggestions-history',
            frameId: frameId
        }
    }, '*');
});
document.getElementById('view-history').onclick = async () => {
    console.log("View History button clicked"); // Debug log
    try {
        showLoading('HISTORY');
        parent.postMessage({
            pluginMessage: {
                type: 'request-history'
            }
        }, '*');
    } catch (error) {
        console.error("Error in view-history handler:", error);
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
        const currentFrame = pages[currentPageIndex];
        const frameNameElement = currentFrame.querySelector('h2');
        const frameName = frameNameElement ? frameNameElement.textContent : 'Unknown Frame';
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







document.getElementById('close-history').addEventListener('click', function() {
    const historyView = document.getElementById('history-view');
    const modificationsScreen = document.getElementById('modifications-screen');
    
    if (historyView && modificationsScreen) {
        historyView.classList.add('hidden');
        modificationsScreen.classList.remove('hidden');
    }
});

console.log("Debugging view history button...");

// Check if button exists


