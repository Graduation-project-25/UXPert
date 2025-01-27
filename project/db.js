const { MongoClient, ObjectId } = require("mongodb");

async function connectToDatabase() {
    const uri = "mongodb://localhost:27017"; // MongoDB connection URI
    const client = new MongoClient(uri);

    try {
        await client.connect();
        console.log("Connected to MongoDB!");
        const db = client.db("FigmaDesign"); // Replace with your database name
        return db;
    } catch (error) {
        console.error("Error connecting to MongoDB:", error);
    }
}


async function insertUser(userData) {
    const db = await connectToDatabase();
    if (!db) {
        console.error("Failed to connect to the database. Exiting...");
        return;
    }

    try {
        const collection = db.collection("users"); 
        const result = await collection.insertOne(userData);
        console.log(`User inserted with ID: ${result.insertedId}`);
        return result.insertedId;  // Return the inserted user's ID
    } catch (error) {
        console.error("Error inserting user data:", error);
    } finally {
        await db.client.close(); 
    }
}


async function insertDesign(userId, designData) {
    const db = await connectToDatabase();
    if (!db) {
        console.error("Failed to connect to the database. Exiting...");
        return;
    }

    try {
        const collection = db.collection("designs"); // Designs collection
        designData.userId = new ObjectId(userId);  // Set the user reference
        const result = await collection.insertOne(designData);
        console.log(`Design inserted with ID: ${result.insertedId}`);
    } catch (error) {
        console.error("Error inserting design data:", error);
    } finally {
        await db.client.close(); // Close the connection
    }
}

async function main() {
    const userData = {
        name: "John Doe",
        email: "john@example.com"
    };

    
    const userId = await insertUser(userData);

    if (userId) {
        const designData = {
            name: "Landing Page",
            features: [
                {
                    type: "Button",
                    position: { x: 100, y: 200 },
                    size: { width: 150, height: 50 },
                    color: "#ff5733",
                    font: "Arial"
                },
                {
                    type: "Text",
                    position: { x: 50, y: 100 },
                    size: { width: 300, height: 100 },
                    color: "#333333",
                    font: "Roboto"
                }
            ]
        };

     
        await insertDesign(userId, designData);
    }
}


main();
