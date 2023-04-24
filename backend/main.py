import os
import re
from typing import Optional

import requests
from dotenv import load_dotenv
from fastapi import Cookie, FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from worker import celery as celery_app
from worker import contributorgrowth, issuegrowth, stargrowth

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


def add_tokens(response: Response, gh_response):
    pattern = r"access_token=([\w-]+)&expires_in=(\d+)&refresh_token=([\w-]+)&refresh_token_expires_in=(\d+)"

    match = re.search(pattern, gh_response.text)

    if match:
        access_token = match.group(1)
        expires_in = int(match.group(2))
        refresh_token = match.group(3)
        refresh_token_expires_in = int(match.group(4))
    else:
        return "API response isn't as expected."

    response.set_cookie(
        key="accesstoken",
        value=access_token,
        httponly=True,
        expires=expires_in,
        # secure=True,
        # samesite="strict",
    )
    response.set_cookie(
        key="refreshtoken",
        value=refresh_token,
        httponly=True,
        expires=refresh_token_expires_in,
        # secure=True,
        # samesite="strict",
    )

    return "You may now close this window."


def fetch_token(response, refreshtoken, accesstoken):
    if refreshtoken and not accesstoken:
        gh_response = requests.post(
            "https://github.com/login/oauth/access_token",
            params={
                "grant_type": "refresh_token",
                "client_id": os.getenv("GITHUB_CLIENT_ID"),
                "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
                "refresh_token": refreshtoken,
            },
        )
        add_tokens(response=response, gh_response=gh_response)


@app.get("/set")
def set_cookie(response: Response):
    response.set_cookie(key="test", value="test")


@app.get("/")
def home(
    test: Optional[str] = Cookie(default=None),
    accesstoken: str = Cookie(default=None),
    refreshtoken: str = Cookie(default=None),
):
    print(accesstoken)
    print(refreshtoken)
    print(test)
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


@app.get("/stargrowth")
def star_growth(
    github_api: str,
    response: Response,
    accesstoken: str = Cookie(default=None),
    refreshtoken: str = Cookie(default=None),
    timedelta: int = 7,
    timedelta_frequency: int = 2,
):
    fetch_token(response, refreshtoken, accesstoken)
    task = stargrowth.delay(
        github_api=github_api,
        access_token=accesstoken,
        timedelta=timedelta,
        timedelta_frequency=timedelta_frequency,
    )
    return JSONResponse({"task_id": task.id})


@app.get("/openissuegrowth")
def open_issue_growth(
    github_api: str,
    response: Response,
    accesstoken: str = Cookie(default=None),
    refreshtoken: str = Cookie(default=None),
    timedelta: int = 7,
    timedelta_frequency: int = 2,
    issue_stats: bool = False,
):
    fetch_token(response, refreshtoken, accesstoken)
    task = issuegrowth.delay(
        github_api=github_api,
        access_token=accesstoken,
        timedelta=timedelta,
        timedelta_frequency=timedelta_frequency,
        issue_stats=issue_stats,
    )
    return JSONResponse({"task_id": task.id})


@app.get("/closedissuegrowth")
def closed_issue_growth(
    github_api: str,
    response: Response,
    accesstoken: str = Cookie(default=None),
    refreshtoken: str = Cookie(default=None),
    timedelta: int = 7,
    timedelta_frequency: int = 2,
):
    fetch_token(response, refreshtoken, accesstoken)
    task = issuegrowth.delay(
        github_api=github_api,
        access_token=accesstoken,
        timedelta=timedelta,
        timedelta_frequency=timedelta_frequency,
        state="closed",
    )
    return JSONResponse({"task_id": task.id})


@app.get("/contributorgrowth")
def contributor_growth(
    github_api: str,
    response: Response,
    timedelta: int = 7,
    timedelta_frequency: int = 2,
    accesstoken: Optional[str] = Cookie(default=None),
    refreshtoken: Optional[str] = Cookie(default=None),
    test: Optional[str] = Cookie(default=None),
):
    print(accesstoken)
    print(refreshtoken)
    print(test)
    fetch_token(response, refreshtoken, accesstoken)
    task = contributorgrowth.delay(
        github_api=github_api,
        access_token=accesstoken,
        timedelta=timedelta,
        timedelta_frequency=timedelta_frequency,
    )
    return JSONResponse({"task_id": task.id})


@app.get("/callback")
def callback(code: str, response: Response, state: str):
    gh_response = requests.post(
        "https://github.com/login/oauth/access_token",
        params={
            "code": code,
            "client_id": os.getenv("GITHUB_CLIENT_ID"),
            "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
        },
    )
    pattern = r"access_token=([\w-]+)&expires_in=(\d+)&refresh_token=([\w-]+)&refresh_token_expires_in=(\d+)"

    match = re.search(pattern, gh_response.text)
    if match:
        access_token = match.group(1)
        expires_in = int(match.group(2))
        refresh_token = match.group(3)
        refresh_token_expires_in = int(match.group(4))
    else:
        return "API response isn't as expected."

    response.set_cookie(
        key="accesstoken",
        value=access_token,
        # httponly=True,
        expires=expires_in,
        # secure=True,
        # samesite="strict",
    )
    response.set_cookie(
        key="refreshtoken",
        value=refresh_token,
        # httponly=True,
        expires=refresh_token_expires_in,
        # secure=True,
        # samesite="strict",
    )

    return "You may now close this window."
    # return add_tokens(response, gh_response)
