// feedbackService.ts
export class FeedbackService {
    async sendFeedbackToBackend(data: any) {
        const processResponse = await fetch("http://localhost:3000/process", {
            method: "POST",
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (!processResponse.ok) {
            throw new Error(`HTTP error! Status: ${processResponse.status}`);
        }

        const result = await processResponse.json();
        return result;  // Consistency, error prevention, and feedback data
    }
}
