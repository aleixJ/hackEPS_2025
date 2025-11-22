# Flask + Vue.js AI Prompt Application

A simple web application with a Flask backend and Vue.js frontend that allows users to input prompts and receive AI-generated outputs.

## Project Structure

```
hackEPS_2025/
├── server/          # Flask backend
└── client/          # Vue.js frontend
```

## Prerequisites

- Python 3.12.3
- Node.js (v16 or higher recommended)
- npm or yarn
- Anaconda (optional, for environment management)

## Setup

### Option 1: Using Anaconda (Recommended)

1. **Create Conda Environment**
   ```bash
   conda create -n hackeps python=3.12.3
   conda activate hackeps
   ```

2. **Install Python Dependencies**
   ```bash
   cd server
   pip install -r requirements.txt
   ```

3. **Install Node Dependencies**
   ```bash
   cd ../client
   npm install
   ```

### Option 2: Using Python venv

1. **Create Virtual Environment**
   ```bash
   python -m venv venv
   ```

2. **Activate Virtual Environment**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

3. **Install Python Dependencies**
   ```bash
   cd server
   pip install -r requirements.txt
   ```

4. **Install Node Dependencies**
   ```bash
   cd ../client
   npm install
   ```

## Running the Application

### Start the Backend (Flask)

1. Activate your environment (conda or venv)
2. Navigate to the server directory:
   ```bash
   cd server
   python app.py
   ```
   The Flask server will start on `http://localhost:5000`

### Start the Frontend (Vue.js)

1. Open a new terminal
2. Navigate to the client directory:
   ```bash
   cd client
   npm run dev
   ```
   The Vue.js development server will start on `http://localhost:5173`

## Usage

1. Open your browser and navigate to `http://localhost:5173`
2. Enter your prompt in the input field
3. Click the "Generate" button to get AI output
4. Use the "Refresh" button to clear the form and start over

## Development

### Backend Structure
- `server/app.py` - Main Flask application
- `server/requirements.txt` - Python dependencies

### Frontend Structure
- `client/src/App.vue` - Main Vue component
- `client/src/main.js` - Vue application entry point
- `client/package.json` - Node dependencies

## API Endpoints

- `POST /api/generate` - Submit a prompt and receive AI-generated output
  - Request body: `{ "prompt": "your prompt here" }`
  - Response: `{ "output": "AI generated response" }`
