from typing import Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from worker import celery as celery_app
from worker import contributorgrowth, issuegrowth, stargrowth

app = FastAPI()


templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "https://github-repo-insights-frontend.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return "Hello, World!"


@app.get("/tasks/{task_id}")
def get_status(task_id: str):
    task_result = celery_app.AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result,
        "progress": task_result.info or {"current": 0, "total": 0},
    }
    if (
        result["task_status"] in ["SUCCESS", "FAILED"]
        and "Not able to access the API" in result["task_result"]
    ):
        result["task_status"] = "FAILED"
        celery_app.control.revoke(task_id)
    return JSONResponse(result)


@app.post("/stargrowth")
def star_growth(
    request: Request,
    github_api: str,
    access_token: Optional[str] = None,
    timedelta: int = 7,
    timedelta_frequency: int = 2,
):
    task = stargrowth.delay(
        github_api=github_api,
        access_token=access_token,
        timedelta=timedelta,
        timedelta_frequency=timedelta_frequency,
    )
    return JSONResponse({"task_id": task.id})


@app.post("/issuegrowth")
def issue_growth(
    request: Request,
    github_api: str,
    access_token: Optional[str] = None,
    timedelta: int = 7,
    timedelta_frequency: int = 2,
    issue_stats: bool = False,
):
    task = issuegrowth.delay(
        github_api=github_api,
        access_token=access_token,
        timedelta=timedelta,
        timedelta_frequency=timedelta_frequency,
        issue_stats=issue_stats,
    )
    return JSONResponse({"task_id": task.id})


@app.post("/contributorgrowth")
def contributor_growth(
    request: Request,
    github_api: str,
    access_token: Optional[str] = None,
    timedelta: int = 7,
    timedelta_frequency: int = 2,
):
    task = contributorgrowth.delay(
        github_api=github_api,
        access_token=access_token,
        timedelta=timedelta,
        timedelta_frequency=timedelta_frequency,
    )
    return JSONResponse({"task_id": task.id})


@app.post("/callback")
def callback(request: Request, code: str):
    print(code)


@app.get("/webhook")
async def github_webhook(request: Request):
    payload = await request.json()
    event_type = request.headers.get("X-Github-Event")
    print(event_type)
    print(payload)
