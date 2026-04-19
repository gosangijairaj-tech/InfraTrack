# Asset Manager

Full-stack asset management app. React + Vite frontend. Python backend. Persistent database.

---

## Tech Stack

| Layer | Tech |
|-------|------|
| Frontend | Pyhton |
| Backend | Python, FastAPI |
| Database | MangoDb Atlas |

---

## Project Structure

```
InfraTrack/
├── backend
│   ├── __init__.py
│   ├── ai_engine.py
│   ├── app.py
│   ├── auth.py
│   ├── dependencies.py
│   ├── error_handlers.py
│   ├── infratrack.log
│   ├── models.py
│   └── routes
│       ├── __init__.py
│       ├── admin_routes.py
│       ├── report_routes.py
│       └── user_routes.py
├── data
│   ├── cat_model.pkl
│   ├── data.csv
│   ├── score_model.pkl
│   ├── train_model.py
│   └── vectorizer.pkl
├── database
│   ├── __init__.py
│   └── db.py
├── frontend
│   ├── __init__.py
│   ├── _pages
│   │   ├── __init__.py
│   │   ├── admin_dashboard.py
│   │   ├── analytics.py
│   │   ├── login.py
│   │   ├── register.py
│   │   ├── submit_report.py
│   │   └── user_dashboard.py
│   ├── components
│   │   └── ui.py
│   ├── main.py
│   └── utils
│       ├── api.py
│       ├── gps.py
│       └── map_utils.py
├── images
│   └── background.jpg
├── infratrack.log
├── optional
│   └── dummy.py
└── requirements.txt
```

---

## Backend Setup (Python)

### Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

**requirements.txt**
```
fastapi
uvicorn
pymongo
pydantic
passlib
python-jose
httpx
streamlit
requests
pandas
plotly

```

### Run server

```bash
uvicorn main:app --reload
```

Server runs at `http://localhost:8000`

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/assets` | List all assets |
| POST | `/assets` | Create new asset |
| GET | `/assets/{id}` | Get single asset |
| PUT | `/assets/{id}` | Update asset |

### Example: `main.py`


## Frontend Setup (React + Vite)

### Install dependencies

```bash
cd frontend
npm install
```

### Run dev server

```bash
streamlit run app.py
```
App runs at `http://localhost:5173`
