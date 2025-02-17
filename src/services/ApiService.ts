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
}
