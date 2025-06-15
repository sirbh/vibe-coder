## Setup

### Requirements

* **Python 3.11 or later**
* **Docker and Docker Compose** (required to run Postgres and other services locally)

Ensure you have Docker installed and running. You can download Docker from [https://www.docker.com/](https://www.docker.com/).

Check your Python version with:

```bash
python3 --version
```

---

### Backend Setup (FastAPI + LangGraph)

#### Start required services with Docker

Use Docker to start the PostgreSQL database:

```bash
docker-compose up -d
```

Make sure the `docker-compose.yml` file includes a Postgres service with credentials that match your `.env`.

#### Create a virtual environment and install dependencies

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

#### Configure environment variables

Create a `.env` file in the root directory with the following content:

```env
HOST="127.0.0.1"
DB_URL="postgresql://vibe_coder_dev:password@localhost:5432/postgres"
OPENAI_API_KEY=
```

#### Start the FastAPI server

Once your environment is activated and dependencies are installed, run:

```bash
uvicorn api:app --reload
```

This will start the backend at:
**[http://localhost:8000](http://localhost:8000)**

---

### Frontend Setup (Next.js or other JS interface)

Navigate to the `interface` folder and install dependencies:

```bash
cd interface
npm install
```

#### Configure environment variables

Create a `.env.local` file in the `interface` folder with the following content:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

#### Start the frontend server

```bash
npm run dev
```

This will start the frontend at:
**[http://localhost:3000](http://localhost:3000)**
