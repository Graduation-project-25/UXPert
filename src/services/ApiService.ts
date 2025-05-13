
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

        
    static async getSuggestions(userData: any, ): Promise<any> {
        try {
            // console.log(`Fetching suggestions for frame ${frameId}`);
            const response = await fetch('http://localhost:3000/get-suggestions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(userData),

            });

            console.log(`Response status: ${response.status}`);
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP error! Status: ${response.status}, Body: ${errorText}`);
            }

            const data = await response.json();
            console.log('Suggestions response:', data);
            return data;
            
        } catch (error) {
            console.error("Error in getSuggestions:", error);
            throw error;
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


    static async getUserHistory(userName: string): Promise<any> {
        try {
            const response = await fetch('http://localhost:3000/get-history', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_name: userName }),
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP error! Status: ${response.status}, Body: ${errorText}`);
            }

            return await response.json();
        } catch (error) {
            console.error("Error getting user history:", error);
            throw error;
        }
    }


}