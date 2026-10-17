# BioResidue - Agricultural Crop Residue Marketplace

BioResidue is a marketplace platform that connects farmers looking to sell crop residue materials with companies needing biomass resources. It provides semantic search queries powered by vector embeddings and Leaflet maps coordinate pinning.

## Tech Stack
- **Backend:** Flask REST API, SQLAlchemy (PostgreSQL / SQLite fallback), ChromaDB (Vector search index), JWT Auth.
- **Frontend:** React.js, Vite, Vanilla CSS (Premium Dark-Glassmorphism layout), Leaflet.js maps.
- **Deployment:** Docker & Docker Compose.

---

## 🚀 Running with Docker (Recommended)

To run the entire stack (PostgreSQL database, Flask API, and React frontend served by Nginx proxy) in containers:

1. Make sure you have Docker running.
2. In the project root folder, execute:
   ```bash
   docker-compose up --build
   ```
3. Open your browser and navigate to:
   **`http://localhost/`** (Runs on standard HTTP port 80).
   *Note: Nginx automatically proxies `/api` calls directly to the Flask service on port 5000 internally.*

---

## 🛠️ Running Locally (Development Mode)

If you don't have Docker installed, you can easily spin up the project locally. The backend will automatically write to a local SQLite database (`backend/app.db`) and configure ChromaDB internally.

### 1. Start the Flask Backend
1. Open a terminal and go to the `backend` folder:
   ```bash
   cd backend
   ```
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *Note: We have decoupled ChromaDB from the local `requirements.txt` to prevent C++ compiler errors on Windows. If run locally, the system automatically falls back to database-driven searches. To run with full semantic vector search, use the Docker configuration.*
4. Start the development server:
   ```bash
   python run.py
   ```
   *The backend will boot on `http://localhost:5000`.*

### 2. Start the React Frontend
1. Open a new terminal and go to the `frontend` folder:
   ```bash
   cd frontend
   ```
2. Install Node packages:
   ```bash
   npm install
   ```
3. Run the Vite development server:
   ```bash
   npm run dev
   ```
   *The frontend will boot on `http://localhost:5173`.*

---

## 🧪 Testing the Walkthrough Flow

To experience the system features:

1. **Sign Up as a Farmer:**
   - Go to registration and select **I am a Farmer**. Create a user (e.g. `farmer_john`).
   - Log in and navigate to **List Residue**.
   - Input crop type (e.g. `Wheat Straw`), quantity (e.g. `20 Tons`), and unit price (e.g. `$45.00/Ton`).
   - Click anywhere on the map component to pin coordinates. Give the region a name (e.g. `Amritsar, Punjab`) and save it.
   - List a few other items (e.g. `Corn Husks` in a different region).

2. **Sign Up as a Company:**
   - Go to registration and select **I am a Company**. Create a user (e.g. `biopower_co`).
   - Navigate to **Browse Residues**.
   - You will see the listings you created on the map.
   - **Try Semantic Search:** Enter descriptions in natural language like `dry stalk for fuel` or `corn waste`. ChromaDB will query the database and rank results by match percentage! *(If running locally without ChromaDB, the system will fall back to standard database text queries showing 100% matches)*.
   - Click **Buy Residue** on a card, enter the quantity you wish to purchase, and submit.

3. **Simulate Mock Payments:**
   - A secure billing checkout overlay will open.
   - Enter card billing details.
   - *Test Payment Failure:* Enter a card number starting with `4000`. The transaction will fail.
   - *Test Payment Success:* Enter any other card number. The transaction will clear, deduct the listing stock, create a transaction record, and update order statuses!
   - Navigate to the **Dashboard** to see the order history and updated metrics.
