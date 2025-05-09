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

    static showDesignModifications(frameId: string, suggestions: string, originalImage: string, modifiedImage: string) {
        console.log("Sending design modifications to UI");
        figma.ui.postMessage({
            type: 'design-modifications',
            frameId,
            suggestions,
            original_image: originalImage,
            modified_image: modifiedImage
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