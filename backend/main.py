from typing import Optional

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from worker import celery as celery_app
from worker import contributorgrowth, issuegrowth, stargrowth
import os
import re

load_dotenv()

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
async def home():
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
async def star_growth(
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


@app.post("/openissuegrowth")
async def open_issue_growth(
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


@app.post("/closedissuegrowth")
async def closed_issue_growth(
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
        state="closed",
    )
    return JSONResponse({"task_id": task.id})


@app.post("/contributorgrowth")
async def contributor_growth(
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


@app.post("/githubaccesstoken")
def github_access_token(request: Request, client_id: str, state: str):
    return requests.post(
        "https://github.com/login/oauth/authorize",
        params={
            "client_id": client_id,
            "state": state,
        },
    )


@app.get("/callback")
async def callback(request: Request, code: str):
    response = requests.post(
        "https://github.com/login/oauth/access_token",
        params={
            "code": code,
            "client_id": os.getenv("GITHUB_CLIENT_ID"),
            "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
        },
    )
    access_token = re.search(r"access_token=(.*?)&", response.text).group(1)
    refresh_token = re.search(r"refresh_token=(.*?)&", response.text).group(1)
    print(access_token)
    return JSONResponse({"access_token": access_token, "refresh_token": refresh_token})
