# Smart Dispatch Agent

A standalone demonstration platform showcasing dynamic fleet vehicle matching and driver allocation using FastAPI and React 19 + TypeScript. Designed as a college presentation mockup.

---

## 🛠️ Tech Stack
* **Frontend**: React 19, Vite, TypeScript, Tailwind CSS v4, Lucide Icons, Axios, React Hook Form
* **Backend**: FastAPI, Pydantic v2, Python

---

## 🚀 Getting Started

### 1. Backend Setup (FastAPI)
Navigate to the `backend/` directory:
```bash
cd backend
```

Create and activate a virtual environment:
* **Windows**:
  ```bash
  python -m venv .venv
  .venv\Scripts\activate
  ```
* **macOS/Linux**:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

Install dependencies:
```bash
pip install -r requirements.txt
```

Start the local mock server on `http://localhost:8000`:
```bash
uvicorn app.main:app --reload
```

---

### 2. Frontend Setup (Vite + React)
Navigate to the `frontend/` directory:
```bash
cd frontend
```

Install dependencies:
```bash
npm install
```

Start the Vite local development server on `http://localhost:5173`:
```bash
npm run dev
```
