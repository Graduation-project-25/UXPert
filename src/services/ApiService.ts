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
    }