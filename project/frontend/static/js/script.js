let currentPageIndex = 0;
const pages = [];
let modifiedDesigns = [];
let feedbackData = {};
let currentModifiedDesignIndex = 0;

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

    // Start feature extraction immediately
    parent.postMessage({ pluginMessage: { type: 'start-detection' } }, '*');

    // No automatic progress increment. We'll wait for messages from the parent.
    const progressInterval = setInterval(() => {
        // This interval will now just keep the UI responsive, but won't increment progress
        if (progress < 100) {
            progressText.textContent = `${progress}%`;
            progressBar.value = progress;
        }
    }, 300);

    // Fallback: Increment progress every 2 seconds if no messages are received, up to 100%
    let fallbackProgress = 0;
    const fallbackInterval = setInterval(() => {
        if (fallbackProgress < 100 && progress < 100) { // Only increment if neither progress is at 100
            fallbackProgress += 10; // Increment by 10% every 2 seconds
            progress = Math.min(fallbackProgress, 100);
            progressBar.value = progress;
            progressText.textContent = `${progress}%`;
            console.log(`Fallback progress: ${progress}%`);
        }
    }, 2000); // 2 seconds interval for fallback

    // Listen for progress or completion messages with debugging
    const messageHandler = (event) => {
        console.log('Message received:', event.data); // Debug: Log all messages
        const msg = event.data.pluginMessage;
        if (!msg) return;

        if (msg.type === 'progress-update') {
            progress = Math.min(msg.progress || 0, 100); // Update progress based on parent's message
            progressBar.value = progress;
            progressText.textContent = `${progress}%`;
            console.log(`Progress updated to: ${progress}%`);

            if (progress >= 100) {
                clearAllIntervalsAndListeners(progressInterval, fallbackInterval, messageHandler);
                jumpToCompletion();
            }
        } else if (msg.type === 'detection-complete') {
            clearAllIntervalsAndListeners(progressInterval, fallbackInterval, messageHandler);
            jumpToCompletion(msg.feedback);
            console.log('Detection complete, jumping to feedback');
        }
    };

    window.addEventListener('message', messageHandler);

    // Fallback timeout: If no completion after 15 seconds, force transition
    const timeout = setTimeout(() => {
        clearAllIntervalsAndListeners(progressInterval, fallbackInterval, messageHandler);
        jumpToCompletion(); // Force transition even without message
        console.log('Timeout triggered, jumping to feedback');
    }, 15000); // 15 seconds timeout

    function clearAllIntervalsAndListeners(progressInt, fallbackInt, handler) {
        clearInterval(progressInt);
        clearInterval(fallbackInt);
        clearTimeout(timeout); // Clear any pending timeout
        window.removeEventListener('message', handler); // Clean up listener
    }

    function jumpToCompletion(feedback = null) {
        // Immediately jump progress to 100% and transition
        progress = 100;
        progressBar.value = progress;
        progressText.textContent = `${progress}%`;

        clearAllIntervalsAndListeners(progressInterval, fallbackInterval, messageHandler); // Ensure everything stops
        document.getElementById('processing-screen').style.display = 'none';
        document.getElementById('feedback-screen').style.display = 'block';

        if (feedback) {
            handleCollectiveFeedback(feedback);
        } else {
            // If no feedback was provided in detection-complete, request it
            parent.postMessage({ pluginMessage: { type: 'request-feedback' } }, '*');
            console.log('Requesting feedback from parent');
        }
    }
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

    if (['Recognition Rather than Recall', 'Aesthetic and Minimalist Design'].includes(currentFeedback.name) && Array.isArray(currentFeedback.data)) {
        currentFeedback.data.forEach(feedbackItem => {
            if (typeof feedbackItem === 'string') {
                html += `<li>${feedbackItem}</li>`;
            } else {
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

// Function to handle collective feedback
function handleCollectiveFeedback(feedback) {
    const pagesContainer = document.getElementById('pages-container');
    pagesContainer.innerHTML = '';
    pages.length = 0;
    feedbackData = {};

    feedback.forEach((item, index) => {
        const frameId = item.frameId || `frame-${index}`;
        const feedbackTypes = getFeedbackTypes(item);

        feedbackData[frameId] = {
            item,
            feedbackTypes,
            currentFeedbackIndex: 0,
            hasModifiedDesign: false
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
            <div id="loading-${frameId}" class="loading" style="display:none;">
                Loading improvements...
            </div>
        `;
        pagesContainer.appendChild(pageSection);
        pages.push(pageSection);
    });

    showPage(0);

    document.querySelectorAll('.feedback-nav-button').forEach(button => {
        button.addEventListener('click', (e) => {
            const frameId = e.currentTarget.getAttribute('data-frame-id');
            navigateFeedback(frameId);
        });
    });

    document.querySelectorAll('.modify-button').forEach(button => {
        button.addEventListener('click', async (e) => {
            const frameId = e.currentTarget.getAttribute('data-frame-id');
            const button = e.currentTarget;
            const loadingIndicator = document.getElementById(`loading-${frameId}`);
            
            button.disabled = true;
            loadingIndicator.style.display = 'block';
            
            parent.postMessage({
                pluginMessage: {
                    type: 'request-modified-design',
                    frameId: frameId
                }
            }, '*');
        });
    });
}

// Message handling
window.addEventListener('message', (event) => {
    console.log('Global message received:', event.data); // Debug: Log all global messages
    const msg = event.data.pluginMessage;
    if (!msg) return;

    if (msg.type === 'collective-feedback') {
        handleCollectiveFeedback(msg.feedback);
    } else if (msg.type === 'design-modified') {
        // Handle the modified design response for a specific frame
        const frameId = msg.frameId;
        const loadingIndicator = document.getElementById(`loading-${frameId}`);
        const modifyButton = document.querySelector(`.modify-button[data-frame-id="${frameId}"]`);
        
        // Hide loading indicator
        if (loadingIndicator) loadingIndicator.style.display = 'none';
        if (modifyButton) modifyButton.disabled = false;
        
        // Store the modified design
        const modifiedDesign = {
            original: msg.original,
            modified: msg.modified,
            modifications: msg.modifications || [],
            design_name: msg.design_name,
            frame_name: msg.frame_name,
            frameId: frameId
        };
        
        // Check if we already have this design
        const existingIndex = modifiedDesigns.findIndex(d => d.frameId === frameId);
        if (existingIndex >= 0) {
            modifiedDesigns[existingIndex] = modifiedDesign;
            currentModifiedDesignIndex = existingIndex;
        } else {
            modifiedDesigns.push(modifiedDesign);
            currentModifiedDesignIndex = modifiedDesigns.length - 1;
        }
        
        // Update the button text
        if (modifyButton) {
            modifyButton.textContent = 'Show Modified Design Again';
        }
        
        // Mark this frame as having a modified design
        if (feedbackData[frameId]) {
            feedbackData[frameId].hasModifiedDesign = true;
        }
        
        // Show the modified design
        showModifiedDesign(currentModifiedDesignIndex);
    }
});

function showModifiedDesign(index) {
    if (modifiedDesigns.length === 0) return;
    
    // Validate index
    if (index < 0) index = modifiedDesigns.length - 1;
    if (index >= modifiedDesigns.length) index = 0;
    currentModifiedDesignIndex = index;
    
    const design = modifiedDesigns[index];
    
    // Update UI
    document.getElementById('feedback-screen').style.display = 'none';
    document.getElementById('modified-design-screen').style.display = 'block';
    
    // Create navigation controls if needed
    if (!document.getElementById('mod-design-navigation')) {
        const navDiv = document.createElement('div');
        navDiv.id = 'mod-design-navigation';
        navDiv.style.display = modifiedDesigns.length > 1 ? 'flex' : 'none';
        navDiv.style.justifyContent = 'center';
        navDiv.style.gap = '10px';
        navDiv.style.margin = '10px 0';
        navDiv.innerHTML = `
            <button id="mod-prev">← Previous</button>
            <span id="mod-design-counter"></span>
            <button id="mod-next">Next →</button>
            <span id="mod-design-name" style="margin-left:10px"></span>
        `;
        document.getElementById('modified-design-screen').prepend(navDiv);
        
        document.getElementById('mod-prev').onclick = () => showModifiedDesign(currentModifiedDesignIndex - 1);
        document.getElementById('mod-next').onclick = () => showModifiedDesign(currentModifiedDesignIndex + 1);
    }
    
    // Update navigation visibility
    document.getElementById('mod-design-navigation').style.display = 
        modifiedDesigns.length > 1 ? 'flex' : 'none';
    
    // Update images
    document.getElementById('original-design-image').src = design.original;
    document.getElementById('modified-design-image').src = design.modified || design.original;
    
    // Update modifications list
    const modList = document.getElementById('modification-list');
    modList.innerHTML = design.modifications?.map(mod => `
        <div class="modification" style="margin:10px 0; padding:10px; border-left:3px solid #4285F4">
            <h4 style="margin:0 0 5px 0; color:#4285F4">${mod.heuristic || 'Improvement'}</h4>
            <p style="margin:5px 0"><strong>Element:</strong> ${mod.node_id}</p>
            <p style="margin:5px 0"><strong>Change:</strong> ${mod.property} → ${mod.value}</p>
            <p style="margin:5px 0"><strong>Reason:</strong> ${mod.reason}</p>
        </div>
    `).join('') || '<p>No modifications details available</p>';
    
    // Update navigation info
    document.getElementById('mod-design-counter').textContent = 
        `Design ${currentModifiedDesignIndex + 1} of ${modifiedDesigns.length}`;
    document.getElementById('mod-design-name').textContent = 
        design.design_name || design.frame_name || '';
}

// Navigation buttons
document.getElementById('prev').onclick = () => showPage(currentPageIndex - 1);
document.getElementById('next').onclick = () => showPage(currentPageIndex + 1);

// Screen transitions
document.getElementById('back-to-feedback-from-mod').onclick = () => {
    document.getElementById('modified-design-screen').style.display = 'none';
    document.getElementById('feedback-screen').style.display = 'block';
    showPage(currentPageIndex);
};

document.getElementById('close').onclick = () => {
    parent.postMessage({ pluginMessage: { type: 'close' } }, '*');
};