let currentPageIndex = 0;
const pages = [];
let modifiedDesigns = [];
let feedbackData = {};
let currentModifiedDesignIndex = 0;
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
        // Store all modified designs (support both single design and array of designs)
        modifiedDesigns = Array.isArray(msg.results) ? msg.results : [{
            original: msg.original,
            modified: msg.modified,
            modifications: msg.modifications || [],
            design_name: msg.design_name,
            frame_name: msg.frame_name
        }];
        
        currentModifiedDesignIndex = Array.isArray(msg.results) ? (msg.currentIndex || 0) : 0;
        
        // Show the modified design screen
        document.getElementById('feedback-screen').style.display = 'none';
        document.getElementById('modified-design-screen').style.display = 'block';
        
        // Create navigation controls if they don't exist
        if (!document.getElementById('mod-design-navigation')) {
            const navDiv = document.createElement('div');
            navDiv.id = 'mod-design-navigation';
            navDiv.style.display = 'none';
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
            
            // Add event listeners
            document.getElementById('mod-prev').onclick = () => {
                showModifiedDesign(currentModifiedDesignIndex - 1);
            };
            document.getElementById('mod-next').onclick = () => {
                showModifiedDesign(currentModifiedDesignIndex + 1);
            };
        }
        
        // Show navigation if multiple designs exist
        const nav = document.getElementById('mod-design-navigation');
        nav.style.display = modifiedDesigns.length > 1 ? 'flex' : 'none';
        
        // Show the current design
        showModifiedDesign(currentModifiedDesignIndex);
    }
    
    function showModifiedDesign(index) {
        // Validate index
        if (index < 0) index = modifiedDesigns.length - 1;
        if (index >= modifiedDesigns.length) index = 0;
        currentModifiedDesignIndex = index;
        
        const design = modifiedDesigns[index];
        
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
        if (document.getElementById('mod-design-counter')) {
            document.getElementById('mod-design-counter').textContent = 
                `Design ${index + 1} of ${modifiedDesigns.length}`;
        }
        if (document.getElementById('mod-design-name')) {
            document.getElementById('mod-design-name').textContent = 
                design.design_name || design.frame_name || '';
        }
    }
});
function showModifiedDesign(index) {
    if (index < 0 || index >= modifiedDesigns.length) return;
    
    currentModifiedDesignIndex = index;
    const design = modifiedDesigns[index];
    
    // Update UI
    document.getElementById('feedback-screen').style.display = 'none';
    document.getElementById('modified-design-screen').style.display = 'block';
    
    // Update design info
    document.getElementById('mod-design-counter').textContent = 
        `Design ${index + 1} of ${modifiedDesigns.length}`;
    document.getElementById('mod-design-name').textContent = 
        design.design_name || design.frameName || `Design ${index + 1}`;
    
    // Update images
    document.getElementById('original-design-image').src = design.original || design.original_image;
    document.getElementById('modified-design-image').src = design.modified || design.modified_image || design.original;
    
    // Update modifications list
    const modList = document.getElementById('modification-list');
    modList.innerHTML = design.modifications?.map(mod => `
        <div class="modification">
            <h4>${mod.heuristic || 'Improvement'}</h4>
            <p><strong>Element:</strong> ${mod.node_id}</p>
            <p><strong>Change:</strong> ${mod.property} → ${mod.value}</p>
            <p><strong>Reason:</strong> ${mod.reason}</p>
        </div>
    `).join('') || '<p>No modifications details available</p>';
}

function showNextModifiedDesign() {
    showModifiedDesign(currentModifiedDesignIndex + 1);
}

function showPrevModifiedDesign() {
    showModifiedDesign(currentModifiedDesignIndex - 1);
}

// Add event listeners
document.getElementById('mod-next').onclick = showNextModifiedDesign;
document.getElementById('mod-prev').onclick = showPrevModifiedDesign;
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
