# EDA Agent 🤖📊

An AI-powered Exploratory Data Analysis agent. Upload your dataset, ask questions in plain English, and get instant insights with auto-generated Python code and visualizations.

## 🌐 Live Demo

**Try it now:** [https://data-analysis-agent-frontend.onrender.com](https://data-analysis-agent-frontend.onrender.com)

> **Note:** The app runs on Render's free tier, so it may take ~30 seconds to wake up on first visit.

<img width="1076" height="707" alt="image" src="https://github.com/user-attachments/assets/808bf68e-cf5b-47e1-ab3e-9126c5de8397" />


---

## ✨ Features

- **Natural Language Queries** - Ask questions about your data in plain English
- **Auto Code Generation** - LangGraph agent generates and executes Python code
- **Rich Visualizations** - Matplotlib, Seaborn, and Plotly charts
- **Secure Sandbox** - Code runs in a safe, isolated environment
- **Session Persistence** - Chat history and plots saved per session
- **Version Control** - Track and switch between dataset versions

---

## 🏗️ Architecture

### Code-First Approach

Unlike traditional chatbots that only provide answers, EDA Agent **generates and executes actual Python code** for every analysis. This ensures:
- **Reproducible results** - All analysis backed by executable code
- **Transparency** - See exactly what code runs for each query
- **Flexibility** - Agent can handle any pandas/matplotlib operation

### LangGraph Orchestration Flow

```
User Query
    ↓
1. Query Understanding (classify intent)
    ↓
2. Code Generation (write Python code)
    ↓
3. Code Validation (safety checks)
    ↓
4. Sandbox Execution (run in isolated env)
    ↓
5. Error Recovery (retry if failed)
    ↓
6. Response Formatting (present results)
    ↓
Code + Plots + Explanation
```

Each step is a LangGraph node, allowing the agent to:
- Make decisions at each stage
- Recover from errors automatically
- Maintain conversation context
- Generate safe, validated code

---

## 🛠️ Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS, Zustand |
| **Backend** | FastAPI, LangGraph, LangChain, Python 3.11+ |
| **LLM** | Groq API (llama-3.3-70b-versatile) |
| **Data** | Pandas, NumPy, Matplotlib, Seaborn, Plotly, Scikit-learn |
| **Deployment** | Docker, Render |

---

## 📁 Project Structure

```
EDA-Agent/
├── backend/
│   ├── app/
│   │   ├── agent/          # LangGraph workflow (nodes.py, prompts.py, workflow.py)
│   │   ├── routers/        # API endpoints (chat.py, upload.py)
│   │   ├── services/       # Business logic (sandbox.py, session.py, summary.py)
│   │   ├── config.py       # Environment configuration
│   │   ├── main.py         # FastAPI app entry
│   │   └── models.py       # Pydantic schemas
│   ├── requirements.txt
│   ├── env.sample          # Environment template
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── lib/            # API client, store, utilities
│   │   └── types/          # TypeScript definitions
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 🚀 Run Locally

### Prerequisites

- Python 3.11+
- Node.js 18+
- [Groq API Key](https://console.groq.com/) (free)

### 1. Clone the Repository

```bash
git clone https://github.com/TusharM24/Data_Analysis-Agent.git
cd Data_Analysis-Agent
```

### 2. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp env.sample .env
# Edit .env and add your GROQ_API_KEY
```

### 3. Setup Frontend

```bash
cd frontend
npm install
```

### 4. Start the App

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python run.py
```
Backend runs at: `http://localhost:8000`

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```
Frontend runs at: `http://localhost:5173`

### Alternative: Docker

```bash
export GROQ_API_KEY=your_key_here
docker-compose up --build
```
App runs at: `http://localhost:3000`

---

## 🧪 Testing the Demo

1. **Open the app** - Visit [https://data-analysis-agent-frontend.onrender.com](https://data-analysis-agent-frontend.onrender.com)

2. **Upload a dataset** - Drag & drop a CSV or Excel file

3. **Ask questions** - Try these example prompts:
   - `"Show me the first 10 rows"`
   - `"What are the column data types?"`
   - `"Create a histogram of [column_name]"`
   - `"Show correlation heatmap"`
   - `"Find missing values in each column"`
   - `"Create a scatter plot of X vs Y"`

4. **View results** - See generated code, explanations, and visualizations

5. **Download** - Save plots as images or download modified datasets

---

## ⚙️ Environment Variables

Create `backend/.env` with:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
DEBUG=true
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- [Groq](https://groq.com/) - Fast LLM inference
- [LangGraph](https://github.com/langchain-ai/langgraph) - Agent orchestration
- [FastAPI](https://fastapi.tiangolo.com/) - Backend framework
- [React](https://react.dev/) + [Vite](https://vitejs.dev/) - Frontend

---

**Made with ❤️ by [Tushar M](https://github.com/TusharM24)**
