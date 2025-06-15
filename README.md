# 🧠 Vibe Coder — Natural Language to Code

An app where users can create full-stack projects by simply describing them in natural language.  
It uses **generative AI (OpenAI + LangGraph + LangChain)** to generate project structure and code.  
The app scaffolds an empty **Next.js** project and incrementally updates it according to the user's input, all in real time.

---

## ⚙️ Setup Guide

### ✅ Requirements

- **Python 3.11 or later**
- **Docker + Docker Compose** (required for running Postgres and other local services)

> 📦 Make sure Docker is installed and running:  
> [https://www.docker.com/](https://www.docker.com/)

Check Python version:

```bash
python3 --version
```

---

### 🚀 Backend Setup (FastAPI + LangGraph)

#### 🔌 Start services with Docker

Start the PostgreSQL service using Docker Compose:

```bash
docker-compose up -d
```

> ✅ Ensure `docker-compose.yml` contains a `postgres` service with matching credentials from your `.env`.

---

#### 🐍 Create virtual environment & install dependencies

**Mac/Linux/WSL:**

```bash
python3 -m venv vibe-code-env
source vibe-code-env/bin/activate
pip install -r requirements.txt
```

**Windows PowerShell:**

```powershell
python3 -m venv vibe-code-env
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
vibe-code-env\Scripts\activate
pip install -r requirements.txt
```

---

#### 🛠 Configure environment variables

Create a `.env` file in the root directory:

```env
HOST="127.0.0.1"
DB_URL="postgresql://vibe_coder_dev:password@localhost:5432/postgres"
OPENAI_API_KEY=
```

> 🔐 Paste your actual OpenAI API key in the `OPENAI_API_KEY` field.

---

#### 🚦 Start FastAPI server

```bash
uvicorn api:app --reload
```

Your backend will be live at:  
**http://localhost:8000**

---

### 💻 Frontend Setup (Next.js UI)

Navigate to the interface directory and install dependencies:

```bash
cd interface
npm install
```

#### 🌐 Configure frontend environment variables

Create `.env.local` inside the `interface` folder:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

#### ▶️ Start the frontend server

```bash
npm run dev
```

Your frontend will be available at:  
**http://localhost:3000**

---

## 📦 Tech Stack

- **Frontend**: Next.js, Tailwind CSS
- **Backend**: FastAPI, LangGraph, LangChain
- **Database**: PostgreSQL (via Docker)
- **LLM**: OpenAI GPT
- **Infra**: Docker, Uvicorn

---

## 🧪 Example Prompt

> "Create a project that displays a form with email and password fields, and shows a welcome message after submission."
