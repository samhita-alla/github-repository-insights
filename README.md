# GitHub Repository Insights

Generate real-time GitHub insights for your open-source projects and stay informed on how your project is progressing.

<img width="1136" alt="Star Growth" src="https://user-images.githubusercontent.com/27777173/234552470-0b3a28a4-5368-4988-b4a1-4731ba76b19c.png">

<img width="845" alt="Open Issue Growth" src="https://user-images.githubusercontent.com/27777173/234552533-29da101b-8090-40bf-9925-bf59dbb59ad5.png">

## 🔥 Features

- Retrieve daily, weekly, and monthly growth figures
- Allows comparison of up to 5 repositories
- Switch repository visibility on/off

## 🏠 Self-host

### Stack

- Vue
- FastAPI
- Celery
- Redis
- Bootstrap

### Prerequisites

- [nvm](https://github.com/nvm-sh/nvm)
- [Redis](https://developer.redis.com/create/homebrew)

### Setup

- Clone this repository
- `nvm install 16`
- Frontend: `cd frontend && npm install && npm run serve`
- The frontend server will be served at http://localhost:8080
- Install requirements: `cd backend && pip install -r requirements.txt`
- Backend: `cd backend && uvicorn main:app --reload`
- The backend server will be served at http://localhost:8000
- Background task: `cd backend && celery --app background_tasks.celery worker --loglevel=info -c 1`
