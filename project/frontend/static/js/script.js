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

// window.addEventListener("message", (event) => {
//     console.log("Received plugin message:", event.data);
// });
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

let modifiedDesigns = [];
let currentDesignIndex = 0;
// window.addEventListener('message', async (event) => {
    
//     const msg = event.data.pluginMessage;
//     console.log("Received message:", msg);

//     if (!msg) {
//         console.error("No pluginMessage found in event data:", event.data);
//         return;
//     }

//     // Handle feedback display
//     if (msg.type === 'collective-feedback') {
//             document.getElementById('processing-screen').style.display = 'none';
//             document.getElementById('feedback-screen').style.display = 'block';
//             const pagesContainer = document.getElementById('pages-container');
//             pagesContainer.innerHTML = '';
    
//             // Group feedback by frameName (page)
//             const feedbackByPage = {};
//             msg.feedback.forEach(item => {
//                 if (!feedbackByPage[item.frameName]) {
//                     feedbackByPage[item.frameName] = [];
//                 }
//                 const feedbacks = [];
//                 ['errorPreventionFeedback', 'consistencyFeedback', 'errorHandlingFeedback', 'minimalistFeedback'].forEach(type => {
//                     if (item[type] && Object.keys(item[type]).length > 0) {
//                         feedbacks.push({ type, data: item[type] });
//                     }
//                 });
//                 feedbackByPage[item.frameName].push({ screenshot: item.screenshot, feedbacks: feedbacks });
//             });
    
//             // Create a section for each page
//             Object.keys(feedbackByPage).forEach((pageName, index) => {
//                 const pageSection = document.createElement('div');
//                 pageSection.className = 'page-section';
//                 pageSection.innerHTML = `<h2>${pageName}</h2>`;
    
//                 const feedbackArea = document.createElement('div');
//                 feedbackArea.className = 'feedback-area';
    
//                 const screenshot = document.createElement('img');
//                 screenshot.src = feedbackByPage[pageName][0].screenshot; // Use the first screenshot
//                 screenshot.className = 'screenshot';
//                 screenshot.alt = `${pageName} Screenshot`;
    
//                 const contentArea = document.createElement('div');
//                 contentArea.className = 'feedback-content';
    
//                 const feedbackDiv = document.createElement('div');
//                 feedbackDiv.id = `feedback-${pageName}`;
    
//                 // Initialize with the first feedback
//                 if (feedbackByPage[pageName][0].feedbacks.length > 0) {
//                     const firstFeedback = feedbackByPage[pageName][0].feedbacks[0];
//                     let feedbackList = '<ul>';
//                     for (const [issue, solution] of Object.entries(firstFeedback.data)) {
//                         feedbackList += `<li><strong>${issue}:</strong> ${solution}</li>`;
//                     }
//                     feedbackList += '</ul>';
//                     feedbackDiv.innerHTML = `<h3>${firstFeedback.type.replace('Feedback', ' Issues')}</h3><div class='divider'></div>${feedbackList}`;
//                 }
    
//                 const navButton = document.createElement('button');
//                 navButton.innerHTML = '→'; // Right arrow
//                 navButton.className = 'feedback-nav-button';
//                 navButton.onclick = () => navigateFeedback(pageName);
    
//                 contentArea.appendChild(feedbackDiv);
//                 contentArea.appendChild(navButton);
    
//                 feedbackArea.appendChild(screenshot);
//                 feedbackArea.appendChild(contentArea);
//                 pageSection.appendChild(feedbackArea);
//                 pagesContainer.appendChild(pageSection);
    
//                 // Store feedback data for navigation
//                 pageFeedbackData[pageName] = feedbackByPage[pageName][0].feedbacks;
//                 if (!currentFeedbackIndex[pageName]) {
//                     currentFeedbackIndex[pageName] = 0;
//                 }
//             });
    
//             // Show the first page
//             showPage(0);
//         }
//         // const msg = event.data.pluginMessage;
    
//         else if (msg.type === 'design-modified') {
//             // Display both images
//             document.getElementById('original-design-image').src = msg.original;
//             document.getElementById('modified-design-image').src = msg.modified_image;

//              // Show modifications
//         const modList = document.getElementById('modification-list');
//         modList.innerHTML = msg.modifications.map(mod => `
//             <div class="modification-item">
//                 <h4>${mod.property} change at (${mod.x},${mod.y})</h4>
//                 <p><strong>New value:</strong> ${mod.new_value}</p>
//                 <p><strong>Reason:</strong> ${mod.reason}</p>
//             </div>
//         `).join('');
        
//         // Show instructions
//         document.getElementById('modification-instructions').innerHTML = `
//             <ul>${msg.instructions.map(i => `<li>${i}</li>`).join('')}</ul>
//         `;
            
//             // Visualize changed regions
//             const canvas = document.createElement('canvas');
//             const ctx = canvas.getContext('2d');
//             const img = new Image();
            
//             img.onload = function() {
//                 canvas.width = img.width;
//                 canvas.height = img.height;
//                 ctx.drawImage(img, 0, 0);
                
//                 // Highlight modified areas
//                 msg.regions.forEach(region => {
//                     ctx.strokeStyle = '#FF0000';
//                     ctx.lineWidth = 2;
//                     ctx.strokeRect(region.x, region.y, region.width, region.height);
                    
//                     ctx.fillStyle = 'rgba(255,0,0,0.1)';
//                     ctx.fillRect(region.x, region.y, region.width, region.height);
//                 });
//                 document.getElementById('feedback-screen').style.display = 'none';
//                 document.getElementById('modified-design-screen').style.display = 'block';
//                 document.getElementById('modification-visualization').appendChild(canvas);
//             };
//             img.src = msg.modified_image;
//         }
    
//     // Handle modified designs
//     // else if (msg.type === 'design-modified') {
//     //     console.log("Design modification data:", {
//     //         original: msg.original,
//     //         modified: msg.modified,
//     //         instructions: msg.instructions
//     //     });

//     //     // Add to modified designs array
//     //     modifiedDesigns.push(msg);
//     //     currentDesignIndex = modifiedDesigns.length - 1;
        
//     //     // Show the modified design screen
//     //     document.getElementById('feedback-screen').style.display = 'none';
//     //     document.getElementById('modified-design-screen').style.display = 'block';
        
//     //     // Display the current design
//     //     await showModifiedDesign(currentDesignIndex);
//     // }
// });


// window.addEventListener('message', (event) => {
//     const msg = event.data.pluginMessage;
    
//     if (msg.type === 'design-modified') {
//         // Show modified design screen
//         document.getElementById('feedback-screen').style.display = 'none';
//         document.getElementById('modified-design-screen').style.display = 'block';
        
//         // Display images
//         document.getElementById('original-design-image').src = msg.original;
//         document.getElementById('modified-design-image').src = msg.modified_image;
        
//         // Display detailed instructions
//         const instructionsContainer = document.getElementById('modification-instructions');
//         instructionsContainer.innerHTML = `
//             <h3>Detailed Improvements</h3>
//             <div class="heuristics-list">
//                 ${msg.instructions.map(instruction => `
//                     <div class="heuristic-item">
//                         <h4>${instruction.heuristic}</h4>
//                         <p><strong>Element:</strong> ${instruction.element}</p>
//                         <div class="comparison">
//                             <div class="before">
//                                 <strong>Before:</strong> ${instruction.before}
//                             </div>
//                             <div class="after">
//                                 <strong>After:</strong> ${instruction.after}
//                             </div>
//                         </div>
//                         <p><strong>Problem:</strong> ${instruction.problem}</p>
//                         <p><strong>Solution:</strong> ${instruction.solution}</p>
//                     </div>
//                 `).join('')}
//             </div>

//         `;
//         const analysisContainer = document.getElementById('analysis-container');
//         analysisContainer.innerHTML = `
//             <h3>Heuristic Analysis</h3>
//             ${msg.analysis.map(item => `
//                 <div class="analysis-item">
//                     <h4>${item.heuristic}</h4>
//                     <p><strong>Element:</strong> ${item.element}</p>
//                     <p><strong>Issue:</strong> ${item.problem}</p>
//                     <p><strong>Solution:</strong> ${item.solution}</p>
//                 </div>
//             `).join('')}
//         `;
    
//     }
// });

//  gpt-4o direct modification trail 
// window.addEventListener('message', (event) => {
//     const msg = event.data.pluginMessage;
    
//     if (msg.type === 'design-modified') {
//         if (msg.error) {
//             // Show error message
//             document.getElementById('error-message').textContent = msg.error;
//             document.getElementById('error-details').textContent = msg.traceback;
//             document.getElementById('error-screen').style.display = 'block';
//             document.getElementById('modified-design-screen').style.display = 'none';
            
//             if (msg.ai_response) {
//                 document.getElementById('ai-response-debug').textContent = msg.ai_response;
//             }
//         } else {
//             // Show modified design
//             document.getElementById('feedback-screen').style.display = 'none';
//             document.getElementById('modified-design-screen').style.display = 'block';
            
//             // Display images
//             document.getElementById('original-design-image').src = msg.original;
//             document.getElementById('modified-design-image').src = msg.modified_image;
            
//             // Display changes
//             const changesList = document.getElementById('changes-list');
//             changesList.innerHTML = msg.changes.map(change => 
//                 `<li>${change.replace('- ', '')}</li>`
//             ).join('');
            
//             // Display full analysis
//             document.getElementById('full-analysis').textContent = msg.analysis;
//         }
//     }
// });


// In your UI message handler
window.addEventListener('message', (event) => {
    const msg = event.data.pluginMessage;
    
    if (msg.type === 'collective-feedback') {
        // Show only feedback screen
        document.getElementById('processing-screen').style.display = 'none';
        document.getElementById('feedback-screen').style.display = 'block';
        
        // Create feedback UI elements
        const pagesContainer = document.getElementById('pages-container');
        pagesContainer.innerHTML = '';
        
        msg.feedback.forEach(item => {
            const pageSection = document.createElement('div');
            pageSection.className = 'page-section';
            pageSection.innerHTML = `
                <h2>${item.frameName}</h2>
                <div class="feedback-area">
                    <img src="${item.screenshot}" class="screenshot" alt="${item.frameName} Screenshot">
                    <div class="feedback-content">
                        <div id="feedback-${item.frameId}">
                            ${renderFeedback(item)}
                        </div>
                        <button class="feedback-nav-button" onclick="navigateFeedback('${item.frameId}')">→</button>
                    </div>
                </div>
                <button class="modify-button" data-frame-id="${item.frameId}">Show Modified Design</button>
            `;
            pagesContainer.appendChild(pageSection);
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
    let html = '';
    const feedbackTypes = [
        { name: 'Error Prevention', data: item.errorPreventionFeedback },
        { name: 'Consistency', data: item.consistencyFeedback },
        { name: 'Error Handling', data: item.errorHandlingFeedback },
        { name: 'Minimalism', data: item.minimalistFeedback },
        { name: 'Recognition', data: item.recognitionFeedback }
    ];
    
    // Show first feedback type by default
    const firstFeedback = feedbackTypes.find(f => Object.keys(f.data).length > 0);
    if (firstFeedback) {
        html += `<h3>${firstFeedback.name} Issues</h3><div class='divider'></div>`;
        html += '<ul>';
        for (const [issue, solution] of Object.entries(firstFeedback.data)) {
            html += `<li><strong>${issue}:</strong> ${solution}</li>`;
        }
        html += '</ul>';
    }
    
    return html;
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
// window.onmessage = (event) => {
//     const msg = event.data.pluginMessage;
//     if (!msg) {
//         console.error("No pluginMessage found in event data:", event.data);
//         return;
//     }
//     if (msg && msg.type === 'collective-feedback') {
//         document.getElementById('processing-screen').style.display = 'none';
//         document.getElementById('feedback-screen').style.display = 'block';
//         const pagesContainer = document.getElementById('pages-container');
//         pagesContainer.innerHTML = '';

//         // Group feedback by frameName (page)
//         const feedbackByPage = {};
//         msg.feedback.forEach(item => {
//             if (!feedbackByPage[item.frameName]) {
//                 feedbackByPage[item.frameName] = [];
//             }
//             const feedbacks = [];
//             ['errorPreventionFeedback', 'consistencyFeedback', 'errorHandlingFeedback', 'minimalistFeedback'].forEach(type => {
//                 if (item[type] && Object.keys(item[type]).length > 0) {
//                     feedbacks.push({ type, data: item[type] });
//                 }
//             });
//             feedbackByPage[item.frameName].push({ screenshot: item.screenshot, feedbacks: feedbacks });
//         });

//         // Create a section for each page
//         Object.keys(feedbackByPage).forEach((pageName, index) => {
//             const pageSection = document.createElement('div');
//             pageSection.className = 'page-section';
//             pageSection.innerHTML = `<h2>${pageName}</h2>`;

//             const feedbackArea = document.createElement('div');
//             feedbackArea.className = 'feedback-area';

//             const screenshot = document.createElement('img');
//             screenshot.src = feedbackByPage[pageName][0].screenshot; // Use the first screenshot
//             screenshot.className = 'screenshot';
//             screenshot.alt = `${pageName} Screenshot`;

//             const contentArea = document.createElement('div');
//             contentArea.className = 'feedback-content';

//             const feedbackDiv = document.createElement('div');
//             feedbackDiv.id = `feedback-${pageName}`;

//             // Initialize with the first feedback
//             if (feedbackByPage[pageName][0].feedbacks.length > 0) {
//                 const firstFeedback = feedbackByPage[pageName][0].feedbacks[0];
//                 let feedbackList = '<ul>';
//                 for (const [issue, solution] of Object.entries(firstFeedback.data)) {
//                     feedbackList += `<li><strong>${issue}:</strong> ${solution}</li>`;
//                 }
//                 feedbackList += '</ul>';
//                 feedbackDiv.innerHTML = `<h3>${firstFeedback.type.replace('Feedback', ' Issues')}</h3><div class='divider'></div>${feedbackList}`;
//             }

//             const navButton = document.createElement('button');
//             navButton.innerHTML = '→'; // Right arrow
//             navButton.className = 'feedback-nav-button';
//             navButton.onclick = () => navigateFeedback(pageName);

//             contentArea.appendChild(feedbackDiv);
//             contentArea.appendChild(navButton);

//             feedbackArea.appendChild(screenshot);
//             feedbackArea.appendChild(contentArea);
//             pageSection.appendChild(feedbackArea);
//             pagesContainer.appendChild(pageSection);

//             // Store feedback data for navigation
//             pageFeedbackData[pageName] = feedbackByPage[pageName][0].feedbacks;
//             if (!currentFeedbackIndex[pageName]) {
//                 currentFeedbackIndex[pageName] = 0;
//             }
//         });

//         // Show the first page
//         showPage(0);
//     }
// };

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
