let currentPageIndex = 0;
let currentFeedbackIndex = {};
let pageCards = {};
let pageFeedbackData = {};


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
    if (currentPageIndex > 0) {
        showPage(currentPageIndex - 1);
    }
};

document.getElementById('next').onclick = () => {
    const pages = document.querySelectorAll('.page-section');
    if (currentPageIndex < pages.length - 1) {
        showPage(currentPageIndex + 1);
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

// In your UI message handler
window.addEventListener('message', (event) => {
    const msg = event.data.pluginMessage;
    
    if (msg.type === 'collective-feedback') {
        // Reset feedback data storage
        pageFeedbackData = {};
        currentFeedbackIndex = {};
        
        // Show only feedback screen
        document.getElementById('processing-screen').style.display = 'none';
        document.getElementById('feedback-screen').style.display = 'block';
        
        // Create feedback UI elements
        const pagesContainer = document.getElementById('pages-container');
        pagesContainer.innerHTML = '';
        
        msg.feedback.forEach(item => {
            const frameId = item.frameId;
            
            // Store all feedback types for this frame
            pageFeedbackData[frameId] = [
                { type: 'Error Prevention', data: item.errorPreventionFeedback },
                { type: 'Consistency', data: item.consistencyFeedback },
                { type: 'Error Handling', data: item.errorHandlingFeedback },
                { type: 'Minimalism', data: item.minimalistFeedback },
                { type: 'Recognition', data: item.recognitionFeedback }
            ].filter(feedback => feedback.data && Object.keys(feedback.data).length > 0);
            
            // Initialize current index for this frame
            currentFeedbackIndex[frameId] = 0;
            
            const pageSection = document.createElement('div');
            pageSection.className = 'page-section';
            pageSection.innerHTML = `
                <h2>${item.frameName}</h2>
                <div class="feedback-area">
                    <img src="${item.screenshot}" class="screenshot" alt="${item.frameName} Screenshot">
                    <div class="feedback-content">
                        <div id="feedback-${frameId}">
                            ${renderFeedback(item)}
                        </div>
                        <button class="feedback-nav-button" data-frame-id="${frameId}">→</button>
                    </div>
                </div>
                <button class="modify-button" data-frame-id="${frameId}">Show Modified Design</button>
            `;
            pagesContainer.appendChild(pageSection);
        });
        
        // Add event listeners to navigation buttons
        document.querySelectorAll('.feedback-nav-button').forEach(button => {
            button.addEventListener('click', (e) => {
                const frameId = e.currentTarget.getAttribute('data-frame-id');
                navigateFeedback(frameId);
            });
        });
        
        // Add event listeners to modify buttons
        document.querySelectorAll('.modify-button').forEach(button => {
            button.addEventListener('click', () => {
                const frameId = button.getAttribute('data-frame-id');
                parent.postMessage({
                    pluginMessage: {
                        type: 'show-modified-design',
                        frameId: frameId
                    }
                }, '*');
            });
        });
    }
    else if (msg.type === 'design-modified') {
        document.querySelectorAll('.screen').forEach(screen => {
            screen.style.display = 'none';
        });
        
        // Then show modified design screen
        const modScreen = document.getElementById('modified-design-screen');
        modScreen.style.display = 'block';
        
        // Only now populate the data
        document.getElementById('original-design-image').src = msg.original;
        document.getElementById('modified-design-image').src = msg.modified;
        
        // Display modifications
        const modList = document.getElementById('modification-list');
        modList.innerHTML = msg.modifications.map(mod => `
            <div class="modification">
                <h4>${mod.heuristic || 'Improvement'}</h4>
                <p><strong>Element:</strong> ${mod.node_id}</p>
                <p><strong>Change:</strong> ${mod.property} → ${mod.value}</p>
                <p><strong>Reason:</strong> ${mod.reason}</p>
            </div>
        `).join('');
    }
});

function renderFeedback(item) {
    // Get the first feedback type that has data
    const feedbackTypes = [
        { type: 'Error Prevention', data: item.errorPreventionFeedback },
        { type: 'Consistency', data: item.consistencyFeedback },
        { type: 'Error Handling', data: item.errorHandlingFeedback },
        { type: 'Minimalism', data: item.minimalistFeedback },
        { type: 'Recognition', data: item.recognitionFeedback }
    ].filter(f => f.data && Object.keys(f.data).length > 0);
    
    if (feedbackTypes.length === 0) return '<p>No feedback available</p>';
    
    const firstFeedback = feedbackTypes[0];
    return `
        <h3>${firstFeedback.type} Issues</h3>
        <div class='divider'></div>
        <ul>
            ${Object.entries(firstFeedback.data).map(([issue, solution]) => 
                `<li><strong>${issue}:</strong> ${solution}</li>`
            ).join('')}
        </ul>
    `;
}

// Error screen button
document.getElementById('retry-button').addEventListener('click', () => {
    document.getElementById('error-screen').style.display = 'none';
    parent.postMessage({ pluginMessage: { type: 'retry-modification' } }, '*');
});
// Handle back button
document.getElementById('back-to-feedback-from-mod').addEventListener('click', () => {
    document.getElementById('modified-design-screen').style.display = 'none';
    document.getElementById('feedback-screen').style.display = 'block';
});
function showPage(index) {
    const pages = document.querySelectorAll('.page-section');
    pages.forEach((page, i) => {
        page.style.display = i === index ? 'block' : 'none';
    });
    currentPageIndex = index;
    document.getElementById('prev').disabled = currentPageIndex === 0;
    document.getElementById('next').disabled = currentPageIndex === pages.length - 1;
}

function navigateFeedback(pageName) {
    const feedbacks = pageFeedbackData[pageName];
    let currentIndex = currentFeedbackIndex[pageName];
    currentIndex = (currentIndex + 1) % feedbacks.length;
    currentFeedbackIndex[pageName] = currentIndex;

    const feedbackDiv = document.getElementById(`feedback-${pageName}`);
    const feedback = feedbacks[currentIndex];
    let feedbackList = '<ul>';
    for (const [issue, solution] of Object.entries(feedback.data)) {
        feedbackList += `<li><strong>${issue}:</strong> ${solution}</li>`;
    }
    feedbackList += '</ul>';
    feedbackDiv.innerHTML = `<h3>${feedback.type.replace('Feedback', ' Issues')}</h3><div class='divider'></div>${feedbackList}`;
}

// Enable arrow key navigation for pages
window.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowLeft') {
        document.getElementById('prev').click();
    } else if (event.key === 'ArrowRight') {
        document.getElementById('next').click();
    }
});
document.getElementById('back-to-feedback-from-mod').addEventListener('click', () => {
    document.getElementById('modified-design-screen').style.display = 'none';
    document.getElementById('feedback-screen').style.display = 'block';
});

document.getElementById('apply-changes').addEventListener('click', () => {
    parent.postMessage({ 
        pluginMessage: { 
            type: 'apply-changes' 
        } 
    }, '*');
});

document.getElementById('discard-changes').addEventListener('click', () => {
    document.getElementById('modified-design-screen').style.display = 'none';
    document.getElementById('feedback-screen').style.display = 'block';
});

// ... in the message handler ...
if (msg.type === 'design-modified') {
    modifiedDesigns.push(msg);
    showModifiedDesign(currentDesignIndex);
}

async function showModifiedDesign(index) {
    const design = modifiedDesigns[index];
    
    // Set original image
    document.getElementById('original-design-image').src = design.original;
    
    // Handle modified image (could be URL or base64)
    const modifiedImg = document.getElementById('modified-design-image');
    if (design.modified.startsWith('data:image')) {
        modifiedImg.src = design.modified;
    } else {
        try {
            // Use our proxy endpoint
            const proxyUrl = `http://localhost:3000/proxy-image?url=${encodeURIComponent(design.modified)}`;
            const response = await fetch(proxyUrl);
            const blob = await response.blob();
            modifiedImg.src = URL.createObjectURL(blob);
        } catch (error) {
            console.error("Failed to load modified image:", error);
            modifiedImg.src = '';
            modifiedImg.alt = 'Failed to load modified design';
        }
    }
    
    // Set instructions
    const instructionsContainer = document.getElementById('modification-instructions-text');
    if (design.instructions && design.instructions.length > 0) {
        instructionsContainer.innerHTML = `<ul>${
            design.instructions.map(i => `<li>${i}</li>`).join('')
        }</ul>`;
    } else {
        instructionsContainer.innerHTML = '<p>No modification instructions provided</p>';
    }
    
    // Update navigation
    document.getElementById('design-counter').textContent = 
        `${index + 1} of ${modifiedDesigns.length}`;
    document.getElementById('prev-design').disabled = index <= 0;
    document.getElementById('next-design').disabled = index >= modifiedDesigns.length - 1;
}
// In your UI code
document.getElementById('show-modified-design').addEventListener('click', (frameId) => {
    parent.postMessage({
        pluginMessage: {
            type: 'show-modified-design',
            frameId: frameId // Pass the specific frame ID
        }
    }, '*');
});
// Navigation buttons
document.getElementById('prev-design').addEventListener('click', () => {
    if (currentDesignIndex > 0) {
        showModifiedDesign(--currentDesignIndex);
    }
});

document.getElementById('next-design').addEventListener('click', () => {
    if (currentDesignIndex < modifiedDesigns.length - 1) {
        showModifiedDesign(++currentDesignIndex);
    }
});
setTimeout(() => {
    document.getElementById('splash-screen').style.display = 'none';
    document.getElementById('initial-screen').style.display = 'block';
}, 2000);
