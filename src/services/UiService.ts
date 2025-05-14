export class UiService {
    private static currentFrameId: string | null = null;
    private static modifiedDesigns: Record<string, { original: string; modified: string; modifications: any[] }> = {};
    private static currentFrameName: string | null = null;

    static setCurrentFrame(frameId: string, frameName: string) {
        this.currentFrameId = frameId;
        this.currentFrameName = frameName;
    }

    static getCurrentFrame() {
        return {
            id: this.currentFrameId,
            name: this.currentFrameName
        };
    }
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

  
    static showSuggestionsHistory(frameId: string, historyItems: any[]) {
    console.log("Showing history with items:", historyItems.length);
    figma.ui.postMessage({
        type: 'suggestions-history-data',
        frameId,
        history: historyItems
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
if (typeof window !== 'undefined') {
    (window as any).UiService = UiService;
}
