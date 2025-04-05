// src/services/ApiService.ts
export class ApiService {
    static async sendToBackend(userData: any) {
        try {
            const response = await fetch("http://localhost:3000/process", {
                method: "POST",
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(userData),
            });

            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

            return await response.json();
        } catch (error) {
            console.error("Error during API request:", error);
            figma.notify(`Failed to send data to backend.`);
            return null;
        }
    }
    static async sendModificationRequest(frameId: string, designData: any) {
        try {
            const response = await fetch("http://localhost:3000/modify-design", {
                method: "POST",
                headers: { 
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    user_name: figma.currentUser?.name || "Unknown",
                    design_name: figma.root.name || "Untitled",
                    frame_id: frameId,
                    design_json: designData,
                    // screenshot: designData.screenshot || ""
                }),
            });
    
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `HTTP error! Status: ${response.status}`);
            }
    
            return await response.json();
        } catch (error) {
            console.error("Modification API error:", error);
            figma.notify("Failed to get design modifications. See console for details.");
            return { 
                status: "error", 
                error: error instanceof Error ? error.message : String(error)
            };
        }
    }
}
