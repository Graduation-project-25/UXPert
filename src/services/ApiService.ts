
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
    static async getSuggestions(frameId: string, designName: string): Promise<any> {
        const response = await fetch('http://localhost:3000/get-suggestions', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ frame_id: frameId, design_name: designName })
        });
        return await response.json();
    }
    
    static async getModifiedImage(frameId: string, designName: string): Promise<any> {
        const response = await fetch('http://localhost:3000/get-modified-image', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ frame_id: frameId, design_name: designName })
        });
        return await response.json();
    }
    static async sendModificationRequest(frameId: string, designData: any): Promise<any> {
        const response = await fetch('http://localhost:3000/modify-design', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(designData)
        });
        const data = await response.json();
        if (data.status === "error") {
            throw new Error(data.message);
        }
        return {
            status: data.result.status,
            modifications: data.result.modifications,
            summary: data.result.summary,
            designJson: data.result.modified_design
        };
    }

    static async checkExistingFrame(frameData: { design_name: string, frame_name: string, elements: any[] }): Promise<any> {
        try {
            const response = await fetch("http://localhost:3000/check-frame", {
                method: "POST",
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(frameData),
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP error! Status: ${response.status}, Body: ${errorText}`);
            }

            const data = await response.json();
            console.log("checkExistingFrame response:", data);
            return data.feedback || null;
        } catch (error) {
            console.error("Error checking existing frame:", error, error instanceof Error ? error.stack : '');
            figma.notify(`Failed to check existing frame data: ${error instanceof Error ? error.message : String(error)}`);
            return null;
        }
    }
}