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

window.addEventListener("message", (event) => {
    console.log("Received plugin message:", event.data);
});
// Handle modified designs
// window.addEventListener('message', event => {
//     const msg = event.data.pluginMessage;
    
//     if (msg.type === 'design-modified') {
//         // Show modified design screen
//         document.getElementById('feedback-screen').style.display = 'none';
//         const modScreen = document.getElementById('modified-design-screen');
//         modScreen.style.display = 'block';
        
//         // Display images
//         document.getElementById('original-design-image').src = msg.original;
//         document.getElementById('modified-design-image').src = msg.modified;
        
//         // Display instructions
//         document.getElementById('modification-instructions-text').innerHTML = 
//             `<ul>${msg.instructions.map(i => `<li>${i}</li>`).join('')}</ul>`;
//     }
// });

// window.addEventListener('message', (event) => {
//     const msg = event.data.pluginMessage;
    
//     if (msg.type === 'design-modified') {
//         // Show modified design screen
//         document.getElementById('feedback-screen').style.display = 'none';
//         const modScreen = document.getElementById('modified-design-screen');
//         modScreen.style.display = 'block';
        
//         // Display images
//         document.getElementById('original-design-image').src = msg.original;
//         document.getElementById('modified-design-image').src = msg.modified;
        
//         // Display instructions
//         const instructionsContainer = document.getElementById('modification-instructions-text');
//         instructionsContainer.innerHTML = msg.instructions 
//             ? `<ul>${msg.instructions.map(i => `<li>${i}</li>`).join('')}</ul>`
//             : '<p>No modification instructions provided</p>';
//     }
// });
window.addEventListener('message', event => {
    const msg = event.data.pluginMessage;
    console.log("Received message:", msg);  // Debug log
    
    if (msg.type === 'design-modified') {
        console.log("Design modification data:", {
            original: msg.original,
            modified: msg.modified,
            instructions: msg.instructions
        });
        
        document.getElementById('feedback-screen').style.display = 'none';
        const modScreen = document.getElementById('modified-design-screen');
        modScreen.style.display = 'block';
        
        const originalImg = document.getElementById('original-design-image');
        const modifiedImg = document.getElementById('modified-design-image');
        
        originalImg.src = msg.original;
        modifiedImg.src = msg.modified;
        console.log("Image URLs set:", originalImg.src, modifiedImg.src);
        
        const instructionsContainer = document.getElementById('modification-instructions-text');
        if (msg.instructions && msg.instructions.length > 0) {
            instructionsContainer.innerHTML = `<ul>${
                msg.instructions.map(i => `<li>${i}</li>`).join('')
            }</ul>`;
        } else {
            instructionsContainer.innerHTML = '<p>No modification instructions provided</p>';
        }
    }
});

// Handle back button
document.getElementById('back-to-feedback-from-mod').addEventListener('click', () => {
    document.getElementById('modified-design-screen').style.display = 'none';
    document.getElementById('feedback-screen').style.display = 'block';
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
        const pagesContainer = document.getElementById('pages-container');
        pagesContainer.innerHTML = '';

        // Group feedback by frameName (page)
        const feedbackByPage = {};
        msg.feedback.forEach(item => {
            if (!feedbackByPage[item.frameName]) {
                feedbackByPage[item.frameName] = [];
            }
            const feedbacks = [];
            ['errorPreventionFeedback', 'consistencyFeedback', 'errorHandlingFeedback', 'minimalistFeedback'].forEach(type => {
                if (item[type] && Object.keys(item[type]).length > 0) {
                    feedbacks.push({ type, data: item[type] });
                }
            });
            feedbackByPage[item.frameName].push({ screenshot: item.screenshot, feedbacks: feedbacks });
        });

        // Create a section for each page
        Object.keys(feedbackByPage).forEach((pageName, index) => {
            const pageSection = document.createElement('div');
            pageSection.className = 'page-section';
            pageSection.innerHTML = `<h2>${pageName}</h2>`;

            const feedbackArea = document.createElement('div');
            feedbackArea.className = 'feedback-area';

            const screenshot = document.createElement('img');
            screenshot.src = feedbackByPage[pageName][0].screenshot; // Use the first screenshot
            screenshot.className = 'screenshot';
            screenshot.alt = `${pageName} Screenshot`;

            const contentArea = document.createElement('div');
            contentArea.className = 'feedback-content';

            const feedbackDiv = document.createElement('div');
            feedbackDiv.id = `feedback-${pageName}`;

            // Initialize with the first feedback
            if (feedbackByPage[pageName][0].feedbacks.length > 0) {
                const firstFeedback = feedbackByPage[pageName][0].feedbacks[0];
                let feedbackList = '<ul>';
                for (const [issue, solution] of Object.entries(firstFeedback.data)) {
                    feedbackList += `<li><strong>${issue}:</strong> ${solution}</li>`;
                }
                feedbackList += '</ul>';
                feedbackDiv.innerHTML = `<h3>${firstFeedback.type.replace('Feedback', ' Issues')}</h3><div class='divider'></div>${feedbackList}`;
            }

            const navButton = document.createElement('button');
            navButton.innerHTML = '→'; // Right arrow
            navButton.className = 'feedback-nav-button';
            navButton.onclick = () => navigateFeedback(pageName);

            contentArea.appendChild(feedbackDiv);
            contentArea.appendChild(navButton);

            feedbackArea.appendChild(screenshot);
            feedbackArea.appendChild(contentArea);
            pageSection.appendChild(feedbackArea);
            pagesContainer.appendChild(pageSection);

            // Store feedback data for navigation
            pageFeedbackData[pageName] = feedbackByPage[pageName][0].feedbacks;
            if (!currentFeedbackIndex[pageName]) {
                currentFeedbackIndex[pageName] = 0;
            }
        });

        // Show the first page
        showPage(0);
    }
};

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
setTimeout(() => {
    document.getElementById('splash-screen').style.display = 'none';
    document.getElementById('initial-screen').style.display = 'block';
}, 2000);
