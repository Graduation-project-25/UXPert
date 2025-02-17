// src/services/UiService.ts
export class UiService {
    static showUI() {
        figma.showUI(__html__, { width: 1024, height: 3024 });
    }

    static sendFeedbackToUI(feedback: any) {
        figma.ui.postMessage({
            type: 'collective-feedback',
            feedback: feedback
        });
    }
}
