

let currentPageIndex = 0;
const pages = [];
let modifiedDesigns = [];
let feedbackData = {};
let currentSuggestions = null;
let currentImages = null;// Store all feedback data per frame
const ApiService = window.ApiService || (function() {
    console.error("ApiService not found!");
    return {
        getModifiedImage: () => Promise.reject("Service not available")
    };
})();

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

    // Start both the progress animation and processing simultaneously
    const progressInterval = setInterval(() => {
        const currentProgress = parseInt(progressBar.value);
        if (currentProgress < 90) { // Only animate up to 90% during processing
            const newProgress = Math.min(currentProgress + 5, 90);
            progressBar.value = newProgress;
            progressText.textContent = `${newProgress}%`;
        }
    }, 300);

    // Start the actual processing
    parent.postMessage({ pluginMessage: { type: 'start-detection' } }, '*');

    // Listen for progress updates from the processing
    const progressListener = (event) => {
        const msg = event.data.pluginMessage;
        if (msg && msg.type === 'progress-update') {
            // Ensure we don't go backwards in progress
            if (msg.progress > progressBar.value) {
                progressBar.value = msg.progress;
                progressText.textContent = `${msg.progress}%`;
            }

            // If processing is complete, finish the progress bar
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

            document.querySelectorAll('modify-button').forEach(button => {
                button.addEventListener('click', (e) => {
                    const frameId = e.currentTarget.getAttribute('data-frame-id');
                    const frameName = feedbackData[frameId].item.frameName;
                    console.log('Requesting modifications for frame:', frameName);
                    showLoading();
                    parent.postMessage({
                        pluginMessage: {
                            type: 'request-modifications',
                            frameName: frameName
                        }
                    }, '*');
                });
            });
        }, 300);
    
    return;
}

if (msg.type === 'design-modifications') {
    hideLoading();
    
    // Clear previous content
    document.getElementById('modification-list').innerHTML = '';
    document.getElementById('modification-summary').innerHTML = '';
    document.getElementById('design-preview').innerHTML = '';
    
    // Handle suggestions
    if (msg.suggestions) {
        document.getElementById('modification-summary').innerHTML = `
            <div class="suggestions-box">
                <h3>Design Suggestions</h3>
                <pre>${msg.suggestions}</pre>
            </div>
        `;
    }

    // Handle image display if available
    if (msg.modified_image && msg.original_image) {
        document.getElementById('design-preview').innerHTML = `
            <h3>Design Comparison</h3>
            <div class="image-comparison">
                <div class="image-container">
                    <h4>Original Design</h4>
                    <img src="${msg.original_image}" class="design-image" style="max-height: none; width: 100%;" />
                </div>
                <div class="image-container">
                    <h4>Modified Design</h4>
                    <img src="data:image/png;base64,${msg.modified_image}" class="design-image" style="max-height: none; width: 100%;" />
                </div>
            </div>
        `;
    }
    
    document.getElementById('modifications-screen').style.display = 'block';
    document.getElementById('feedback-screen').style.display = 'none';
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
    console.log("Modify button clicked"); // Debug log
    // showLoading();
    document.getElementById('feedback-screen').innerHTML = 'Loading...';
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
        console.log("Requesting modifications for frame:", frameName); // Debug log
        
        // Send message to Figma plugin
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


// function showModifications(data) {
//     try {
//         console.log("Showing modifications:", data);
        
//         // Hide other screens
//         document.getElementById('processing-screen').style.display = 'none';
//         document.getElementById('feedback-screen').style.display = 'none';
        
//         const modScreen = document.getElementById('modifications-screen');
//         const modList = document.getElementById('modification-list');
//         const summaryEl = document.getElementById('modification-summary');
        
//         // Clear previous content
//         modList.innerHTML = '';
//         summaryEl.innerHTML = '';

//         // Handle different response structures
//         if (data.suggestions) {
//             summaryEl.innerHTML = `
//                 <div class="suggestions-box">
//                     <h3>Design Suggestions</h3>
//                     <pre>${data.suggestions}</pre>
//                     ${data.image ? '' : `<button id="show-modified-image" class="button">Show Modified Image</button>`}
//                 </div>
//             `;
//         } else if (data.summary) {
//             summaryEl.innerHTML = `
//                 <div class="summary-box">
//                     <h3>Design Assessment Summary</h3>
//                     <p>${data.summary}</p>
//                 </div>
//             `;
//         }

//         // Handle modifications list
//         if (data.modifications && data.modifications.length > 0) {
//             const modList = document.getElementById('modification-list');
//             modList.innerHTML = '';
            
//             const fragment = document.createDocumentFragment();
            
//             data.modifications.forEach(mod => {
//                 const modItem = document.createElement('div');
//                 modItem.className = 'modification-item';
                
//                 // Extract element details with fallbacks
//                 const elementId = mod.element_id || mod.id || 'unknown';
//                 const elementType = mod.type || 'element';
//                 const elementName = mod.element_name || mod.text || `Untitled ${elementType}`;
//                 const changes = mod.changes || mod.modifications || [];
//                 const heuristic = mod.heuristic || 'General Improvement';
//                 const severity = mod.severity || 'medium';
                
//                 // Create severity indicator
//                 const severityIndicator = document.createElement('div');
//                 severityIndicator.className = `severity-indicator ${severity}`;
//                 severityIndicator.title = `Severity: ${severity}`;
                
//                 modItem.innerHTML = `
//                     <div class="element-header">
//                         <h4>${elementName}</h4>
//                         <span class="element-type">${elementType}</span>
//                         <span class="element-id">ID: ${elementId}</span>
//                         <div class="heuristic-tag">${heuristic}</div>
//                     </div>
//                     <div class="modification-details">
//                         ${changes.length > 0 ? 
//                             changes.map(change => `
//                                 <div class="change-item">
//                                     <div class="change-header">
//                                         <div class="change-property">${change.property || 'Property'}:</div>
//                                         ${change.heuristic ? `<div class="heuristic-tag small">${change.heuristic}</div>` : ''}
//                                     </div>
//                                     <div class="change-from-to">
//                                         <span class="from">${change.from || 'Current'}</span>
//                                         <span class="arrow">→</span>
//                                         <span class="to">${change.to || 'Suggested'}</span>
//                                     </div>
//                                     ${change.reason ? `<div class="change-reason">${change.reason}</div>` : ''}
//                                     ${change.example ? `<div class="change-example"><strong>Example:</strong> ${change.example}</div>` : ''}
//                                 </div>
//                             `).join('') :
//                             `<div class="no-changes">No specific changes suggested for this element</div>`
//                         }
//                     </div>
//                 `;
                
//                 // Add severity indicator to the header
//                 const header = modItem.querySelector('.element-header');
//                 header.insertBefore(severityIndicator, header.firstChild);
                
//                 fragment.appendChild(modItem);
//             });
            
//             modList.appendChild(fragment);
            
//             // Add CSS for new elements if not already present
//             const style = document.createElement('style');
//             style.textContent = `
//                 .severity-indicator {
//                     width: 12px;
//                     height: 12px;
//                     border-radius: 50%;
//                     margin-right: 8px;
//                     display: inline-block;
//                 }
//                 .severity-indicator.high {
//                     background-color: #ff4d4f;
//                 }
//                 .severity-indicator.medium {
//                     background-color: #faad14;
//                 }
//                 .severity-indicator.low {
//                     background-color: #52c41a;
//                 }
//                 .heuristic-tag {
//                     display: inline-block;
//                     background-color: #f0f0f0;
//                     padding: 2px 8px;
//                     border-radius: 4px;
//                     font-size: 0.8em;
//                     margin-left: 8px;
//                     color: #666;
//                 }
//                 .heuristic-tag.small {
//                     font-size: 0.7em;
//                     margin-left: 6px;
//                 }
//                 .change-header {
//                     display: flex;
//                     align-items: center;
//                     margin-bottom: 4px;
//                 }
//                 .change-property {
//                     font-weight: bold;
//                     margin-right: 8px;
//                 }
//                 .change-from-to {
//                     display: flex;
//                     align-items: center;
//                     margin: 4px 0;
//                 }
//                 .arrow {
//                     margin: 0 8px;
//                     color: #888;
//                 }
//                 .change-reason {
//                     font-size: 0.9em;
//                     color: #666;
//                     margin-top: 4px;
//                     font-style: italic;
//                 }
//                 .change-example {
//                     font-size: 0.85em;
//                     background: #f8f8f8;
//                     padding: 6px;
//                     border-radius: 4px;
//                     margin-top: 6px;
//                     border-left: 3px solid #1890ff;
//                 }
//             `;
//             if (!document.querySelector('style.severity-styles')) {
//                 style.className = 'severity-styles';
//                 document.head.appendChild(style);
//             }
//         } else {
//             document.getElementById('modification-list').innerHTML = `
//                 <div class="no-modifications">
//                     <p>No specific modifications suggested.</p>
//                     ${data.suggestions ? 
//                         '<p>Review the suggestions above for general improvements.</p>' : 
//                         '<p>Try analyzing the design again.</p>'
//                     }
//                 </div>
//             `;
//         }

//         // Handle image display
//         const designPreview = document.getElementById('design-preview');
//         if (data.image) {
//             designPreview.innerHTML = `
//                 <h3>Modified Design Preview</h3>
//                 <img src="${data.image}" class="design-image" />
//             `;
//         } else if (data.original_image && data.modified_image) {
//             designPreview.innerHTML = `
//                 <h3>Design Comparison</h3>
//                 <div class="image-comparison">
//                     <div class="image-container">
//                         <h4>Original Design</h4>
//                         <img src="${data.original_image}" class="design-image" />
//                     </div>
//                     <div class="image-container">
//                         <h4>Modified Design</h4>
//                         <img src="data:image/png;base64,${data.modified_image}" class="design-image" />
//                     </div>
//                 </div>
//             `;
//         }

//         modScreen.style.display = 'block';
        
//     } catch (error) {
//         console.error("Error showing modifications:", error);
//         document.getElementById('error-message').textContent = "Could not display modifications";
//         document.getElementById('error-details').textContent = error.stack;
//         document.getElementById('error-screen').style.display = 'block';
//     }
// }