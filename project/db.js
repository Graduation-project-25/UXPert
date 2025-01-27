const { MongoClient } = require("mongodb");

async function connectToDatabase() {
    const uri = "mongodb://localhost:27017"; 
    const client = new MongoClient(uri);

    try {
        await client.connect();
        console.log("Connected to MongoDB!");
        const db = client.db("FigmaDesign");
        return db;
    } catch (error) {
        console.error("Error connecting to MongoDB:", error);
    } finally {
        await client.close(); 
    }
}
const connectToDatabase = require('./db');

async function saveDesign(userId, designData) {
  const db = await connectToDatabase();
  const designsCollection = db.collection('designs');
  const usersCollection = db.collection('users');

  const { name, thumbnailUrl, features } = designData;

  const newDesign = {
    user_id: userId,
    name,
    thumbnailUrl,
    features,
    created_at: new Date(),
    updated_at: new Date(),
  };

  // Insert design into the database
  const result = await designsCollection.insertOne(newDesign);

  // Update user's designs
  await usersCollection.updateOne(
    { _id: userId },
    { $push: { designs: result.insertedId } },
    { upsert: true }
  );

  console.log('Design saved with ID:', result.insertedId);
}

connectToDatabase();
