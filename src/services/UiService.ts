export class UiService {
    private static currentFrameId: string | null = null;
    private static modifiedDesigns: Record<string, { original: string; modified: string; modifications: any[] }> = {};

    static showUI() {
        figma.showUI(__html__, { 
            width: 1024, 
            height: 3024,
            themeColors: true
        });
    }

    static sendFeedbackToUI(feedback: any) {
        figma.ui.postMessage({
            type: 'collective-feedback',
            feedback: feedback
        });
    }

    static showModifiedDesign(frameId: string, original: string, modified: string, modifications: any[]) {
        // Store the modified design for this frame
        this.modifiedDesigns[frameId] = {
            original,
            modified,
            modifications
        };
        
        // Send to UI
        figma.ui.postMessage({
            type: 'design-modifications',
            frameId,
            original,
            modified,
            modifications
        });
    }

    static getModifiedDesign(frameId: string) {
        return this.modifiedDesigns[frameId] || null;
    }

    static getCurrentFrameId() {
        return this.currentFrameId;
    }

    static setCurrentFrameId(frameId: string) {
        this.currentFrameId = frameId;
    }
}