# EDA Agent 🤖📊

An intelligent Exploratory Data Analysis agent that generates and executes Python code to analyze your datasets. Built with FastAPI, LangGraph, React, and Groq's blazing-fast LLM inference.

![Architecture](https://img.shields.io/badge/Architecture-FastAPI%20%2B%20LangGraph%20%2B%20React-blue)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![TypeScript](https://img.shields.io/badge/TypeScript-5.3+-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

- **Natural Language Interface** - Ask questions about your data in plain English
- **Automatic Code Generation** - Agent generates Python code for analysis using LangGraph workflow
- **Secure Execution** - Code runs in a sandboxed environment with safety validations
- **Rich Visualizations** - Matplotlib, Seaborn, and Plotly charts
- **Session Management** - Persistent conversation history with multi-session support
- **Smart Error Recovery** - Automatic error handling and code regeneration
- **Beautiful UI** - Modern React interface with Tailwind CSS and dark theme
- **Docker Support** - Easy deployment with Docker Compose

## 🎯 Use Cases

- **Quick Data Exploration** - Upload a dataset and get instant insights
- **Statistical Analysis** - Perform correlation analysis, hypothesis testing, and more
- **Data Visualization** - Generate publication-ready plots and charts
- **Anomaly Detection** - Identify outliers and unusual patterns
- **Data Quality Assessment** - Check for missing values, duplicates, and inconsistencies
- **Time Series Analysis** - Analyze trends and patterns over time

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React + TypeScript)             │
├─────────────────────────────────────────────────────────────┤
│  File Upload │ Dataset Summary │ Chat Interface │ Plot Gallery │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTP/REST API
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                         │
├─────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────┐ │
│  │                 LangGraph Agent Workflow                │ │
│  │  1. Query Understanding → 2. Code Generation →         │ │
│  │  3. Code Validation → 4. Sandbox Execution →          │ │
│  │  5. Error Recovery → 6. Response Formatting           │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────┐  ┌───────────────┐  ┌───────────────┐  │
│  │ Session Manager│  │ Code Sandbox  │  │ File Storage  │  │
│  └────────────────┘  └───────────────┘  └───────────────┘  │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
                   ┌──────────────────────┐
                   │   Groq API (LLM)     │
                   │  (llama-3.3-70b)     │
                   └──────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **Groq API Key** - [Get yours free](https://console.groq.com/)

### Option 1: Local Development

#### 1. Clone and Setup Backend

```bash
# Navigate to project directory
cd "EDA Agent"

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
cp env.sample .env
# Edit .env and add your GROQ_API_KEY
```

#### 2. Start Backend Server

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python run.py
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

#### 3. Start Frontend Development Server

In a new terminal:

```bash
cd frontend
npm install
npm run dev
```

The UI will be available at `http://localhost:5173`

### Option 2: Docker Deployment (Recommended)

```bash
# Set your Groq API key
export GROQ_API_KEY=your_key_here

# Build and run with Docker Compose
docker-compose up --build

# Access the app at http://localhost:3000
```

To run in detached mode:
```bash
docker-compose up -d
```

To stop:
```bash
docker-compose down
```

## 📖 API Reference

### Upload Dataset

```bash
POST /api/upload
Content-Type: multipart/form-data

# Form data
file: <your-csv-or-excel-file>

# Response
{
  "session_id": "uuid-here",
  "filename": "data.csv",
  "summary": {
    "shape": [100, 5],
    "columns": ["col1", "col2", ...],
    "dtypes": {...},
    "missing_values": {...}
  }
}
```

### Send Message

```bash
POST /api/chat
Content-Type: application/json

{
  "session_id": "uuid-here",
  "message": "Show me a histogram of the age column"
}

# Response
{
  "response": "I've created a histogram...",
  "code": "import matplotlib.pyplot as plt\n...",
  "plots": ["session_id_plot_id.png"],
  "execution_result": {...}
}
```

### Get Session Info

```bash
GET /api/session/{session_id}

# Response
{
  "session_id": "uuid-here",
  "dataset_path": "/path/to/data.csv",
  "dataset_info": {...},
  "messages": [...]
}
```

### List All Sessions

```bash
GET /api/sessions

# Response
{
  "sessions": [
    {
      "session_id": "uuid-1",
      "created_at": "2024-01-01T00:00:00",
      "message_count": 5
    }
  ]
}
```

### Get Plot

```bash
GET /api/plots/{filename}

# Returns the plot image
```

## 💡 Example Prompts

Here are some example questions you can ask the EDA Agent:

### Basic Statistics
- "Show me a summary of the dataset"
- "What are the basic statistics for all numerical columns?"
- "How many missing values are there in each column?"
- "What's the data type of each column?"

### Visualizations
- "Create a histogram of the age column"
- "Show a scatter plot of price vs quantity"
- "Generate a correlation heatmap"
- "Create a box plot to show outliers in the salary column"
- "Show the distribution of the 'category' column as a pie chart"

### Analysis
- "What are the top 10 customers by total sales?"
- "Find outliers in the revenue column"
- "What are the correlations between numerical columns?"
- "Show me the trend of sales over time"
- "Calculate the percentage of missing values"

### Advanced Queries
- "Perform a group-by analysis on category and show mean values"
- "Create a pair plot for all numerical columns"
- "Show me the relationship between variables X and Y with a regression line"
- "Identify and visualize duplicate rows"

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the `backend` directory:

| Variable | Description | Default |
|----------|-------------|---------|
| `GROQ_API_KEY` | Your Groq API key (required) | - |
| `GROQ_MODEL` | LLM model to use | `llama-3.3-70b-versatile` |
| `DEBUG` | Enable debug mode | `true` |
| `EXECUTION_TIMEOUT` | Code execution timeout (seconds) | `30` |
| `MAX_FILE_SIZE` | Max upload size (bytes) | `52428800` (50MB) |
| `UPLOAD_DIR` | Directory for uploaded files | `./data/uploads` |
| `PLOTS_DIR` | Directory for generated plots | `./data/plots` |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000,http://localhost:5173` |

## 🛡️ Security

The code execution sandbox includes multiple layers of protection:

### Code Validation
- **Pattern Blocking** - Prevents dangerous operations (os.system, subprocess, exec, eval, etc.)
- **Import Restrictions** - Only allows whitelisted data science libraries
- **Syntax Checking** - Validates Python syntax before execution

### Runtime Protection
- **Timeout Protection** - Kills long-running code after 30 seconds
- **File Isolation** - Code can only access the uploaded dataset
- **Memory Limits** - Prevents memory exhaustion attacks
- **Error Recovery** - Automatic error handling and code regeneration

### Allowed Operations
✅ Data manipulation with pandas/numpy  
✅ Statistical analysis  
✅ Visualization with matplotlib/seaborn/plotly  
✅ Machine learning with scikit-learn  

### Blocked Operations
❌ File system operations (except reading the dataset)  
❌ Network requests  
❌ System commands  
❌ Code compilation/execution  
❌ Process manipulation  

## 📦 Tech Stack

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **LangGraph** - Framework for building stateful agent workflows
- **LangChain** - LLM orchestration and prompt management
- **Groq** - Ultra-fast LLM inference (llama-3.3-70b-versatile)
- **Pandas** - Data manipulation and analysis
- **Matplotlib/Seaborn/Plotly** - Data visualization
- **Scikit-learn** - Machine learning utilities

### Frontend
- **React 18** - UI library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Zustand** - Lightweight state management
- **Axios** - HTTP client
- **React Markdown** - Markdown rendering
- **Lucide React** - Icon library
- **Framer Motion** - Animation library

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Nginx** - Frontend web server (in production)

## 📦 Pre-installed Libraries

The sandbox environment has these libraries pre-configured:

- **Data Processing**: pandas, numpy, scipy
- **Visualization**: matplotlib, seaborn, plotly
- **Machine Learning**: scikit-learn, statsmodels
- **Utilities**: json, datetime, math, collections, re

## 🗂️ Project Structure

```
EDA Agent/
├── backend/
│   ├── app/
│   │   ├── agent/
│   │   │   ├── nodes.py          # LangGraph node implementations
│   │   │   ├── prompts.py        # LLM prompt templates
│   │   │   └── workflow.py       # Agent workflow definition
│   │   ├── routers/
│   │   │   ├── chat.py           # Chat endpoints
│   │   │   └── upload.py         # File upload endpoints
│   │   ├── services/
│   │   │   ├── sandbox.py        # Code execution sandbox
│   │   │   ├── session.py        # Session management
│   │   │   └── summary.py        # Dataset analysis
│   │   ├── config.py             # Configuration management
│   │   ├── main.py               # FastAPI application
│   │   └── models.py             # Pydantic data models
│   ├── data/
│   │   ├── uploads/              # Uploaded datasets
│   │   └── plots/                # Generated visualizations
│   ├── Dockerfile
│   ├── requirements.txt          # Python dependencies
│   ├── env.sample                # Environment variables template
│   └── run.py                    # Application entry point
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInterface.tsx    # Chat UI component
│   │   │   ├── DatasetSummary.tsx   # Dataset info display
│   │   │   ├── FileUpload.tsx       # File upload component
│   │   │   └── PlotGallery.tsx      # Plot display gallery
│   │   ├── lib/
│   │   │   ├── api.ts               # API client functions
│   │   │   ├── store.ts             # Zustand state management
│   │   │   └── utils.ts             # Utility functions
│   │   ├── types/
│   │   │   └── index.ts             # TypeScript type definitions
│   │   ├── App.tsx                  # Main application component
│   │   ├── main.tsx                 # React entry point
│   │   └── index.css                # Global styles
│   ├── public/
│   ├── Dockerfile
│   ├── nginx.conf                   # Nginx configuration
│   ├── package.json                 # Node dependencies
│   ├── tsconfig.json                # TypeScript configuration
│   ├── tailwind.config.js           # Tailwind CSS configuration
│   └── vite.config.ts               # Vite build configuration
├── docker-compose.yml               # Docker Compose configuration
└── README.md                        # This file
```

## 🔍 How It Works

### LangGraph Agent Workflow

The agent follows a sophisticated multi-step workflow:

1. **Query Understanding** - Analyzes the user's intent and classifies the query type
2. **Code Generation** - Generates appropriate Python code based on the query
3. **Code Validation** - Validates code safety and syntax before execution
4. **Sandbox Execution** - Runs the code in a secure sandboxed environment
5. **Error Recovery** - If execution fails, attempts to fix and regenerate code
6. **Response Formatting** - Formats the results into a user-friendly response

### Workflow Graph

```
┌──────────────────┐
│ Understand Query │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Generate Code   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Validate Code   │
└────────┬─────────┘
         │
    ┌────┴────┐
    │ Valid?  │
    └─┬────┬──┘
  Yes │    │ No
      │    └──────┐
      ▼           ▼
┌──────────┐  ┌──────────────┐
│ Execute  │  │ Handle Error │
│   Code   │  └──────────────┘
└────┬─────┘
     │
     ▼
┌──────────────────┐
│ Format Response  │
└──────────────────┘
```

## 🐛 Troubleshooting

### Backend Issues

**Issue**: `GROQ_API_KEY not set` warning
```bash
# Solution: Make sure you've created .env file and added your API key
cp backend/env.sample backend/.env
# Edit .env and add: GROQ_API_KEY=your_key_here
```

**Issue**: Module not found errors
```bash
# Solution: Ensure virtual environment is activated and dependencies are installed
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

**Issue**: Port 8000 already in use
```bash
# Solution: Kill the process using port 8000 or change the port
# On macOS/Linux:
lsof -ti:8000 | xargs kill -9
# Or modify run.py to use a different port
```

### Frontend Issues

**Issue**: Cannot connect to backend
```bash
# Solution: Check backend is running and update API URL if needed
# Backend should be at http://localhost:8000
# Check frontend/src/lib/api.ts for API_URL configuration
```

**Issue**: npm install fails
```bash
# Solution: Clear npm cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

### Docker Issues

**Issue**: Docker build fails
```bash
# Solution: Ensure Docker daemon is running and try rebuilding
docker-compose down
docker-compose build --no-cache
docker-compose up
```

**Issue**: Permission errors in Docker volumes
```bash
# Solution: Fix permissions on data directories
sudo chown -R $USER:$USER ./data
```

## 🚦 Development Tips

### Hot Reload
- **Backend**: FastAPI automatically reloads on code changes when using `uvicorn` with `--reload`
- **Frontend**: Vite provides instant HMR (Hot Module Replacement)

### Debugging
- Check backend logs for detailed error messages
- Use FastAPI's interactive docs at `http://localhost:8000/docs`
- Enable DEBUG mode in `.env` for verbose logging
- Use browser DevTools to inspect API requests and responses

### Testing Prompts
Start with simple prompts and gradually increase complexity:
1. "Show me the first 5 rows"
2. "What are the column names?"
3. "Create a histogram of column X"
4. "Show correlation between X and Y"

## 🗺️ Roadmap

Future enhancements planned:

- [ ] Support for more file formats (JSON, Parquet, SQL databases)
- [ ] Advanced statistical tests (t-tests, ANOVA, chi-square)
- [ ] Export analysis reports (PDF, HTML)
- [ ] Collaborative sessions with sharing
- [ ] Pre-built analysis templates
- [ ] Integration with additional LLM providers
- [ ] Custom visualization themes
- [ ] Real-time streaming responses
- [ ] Multi-file analysis support
- [ ] Version control for analysis history

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please ensure your PR:
- Follows the existing code style
- Includes appropriate tests
- Updates documentation as needed
- Has a clear description of changes

## 📄 License

This project is licensed under the MIT License - see below for details:

```
MIT License

Copyright (c) 2024 EDA Agent Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🙏 Acknowledgments

- [Groq](https://groq.com/) - For providing blazing-fast LLM inference
- [LangGraph](https://github.com/langchain-ai/langgraph) - For the agent orchestration framework
- [LangChain](https://www.langchain.com/) - For LLM integration tools
- [FastAPI](https://fastapi.tiangolo.com/) - For the amazing backend framework
- [React](https://react.dev/) - For the powerful UI library
- [Vite](https://vitejs.dev/) - For the lightning-fast build tool
- [Tailwind CSS](https://tailwindcss.com/) - For the utility-first CSS framework

## 📞 Support

If you encounter any issues or have questions:

- Open an issue on GitHub
- Check the [Troubleshooting](#-troubleshooting) section
- Review the API documentation at `http://localhost:8000/docs`

---

**Made with ❤️ for data scientists and analysts**

⭐ Star this repo if you find it helpful!
