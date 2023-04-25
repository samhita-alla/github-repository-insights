# GitHub Repository Insights

Generate real-time GitHub insights for your open-source projects and stay informed on how your project is progressing.

## 🔥 Features

- Retrieve daily, weekly, and monthly growth figures
- Allows comparison of up to 5 repositories
- Switch repository visibility on/off

## 🛠️ Development

### Stack

- Vue
- FastAPI
- Bootstrap
- Celery
- Redis

### Prerequisites

- [nvm](https://github.com/nvm-sh/nvm)
- [Redis](https://developer.redis.com/create/homebrew)

### Setup

- `nvm install 16`
- Frontend: `cd frontend && npm install && npm run serve`
- The frontend server will be served at http://localhost:8080.
- Backend: `cd backend && pip install -r requirements.txt && uvicorn main:app --reload`
- The backend server will be served at http://localhost:8000
- Background task: `celery --app worker.celery worker --loglevel=info -c 1`
