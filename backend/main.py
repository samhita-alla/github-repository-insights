import os
import re
from typing import Optional

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response, Cookie
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
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
    accesstoken: str = Cookie(None),
    timedelta: int = 7,
    timedelta_frequency: int = 2,
):
    task = stargrowth.delay(
        github_api=github_api,
        access_token=accesstoken,
        timedelta=timedelta,
        timedelta_frequency=timedelta_frequency,
    )
    return JSONResponse({"task_id": task.id})


@app.post("/openissuegrowth")
async def open_issue_growth(
    request: Request,
    github_api: str,
    accesstoken: str = Cookie(None),
    timedelta: int = 7,
    timedelta_frequency: int = 2,
    issue_stats: bool = False,
):
    task = issuegrowth.delay(
        github_api=github_api,
        access_token=accesstoken,
        timedelta=timedelta,
        timedelta_frequency=timedelta_frequency,
        issue_stats=issue_stats,
    )
    return JSONResponse({"task_id": task.id})


@app.post("/closedissuegrowth")
async def closed_issue_growth(
    request: Request,
    github_api: str,
    accesstoken: str = Cookie(None),
    timedelta: int = 7,
    timedelta_frequency: int = 2,
    issue_stats: bool = False,
):
    task = issuegrowth.delay(
        github_api=github_api,
        access_token=accesstoken,
        timedelta=timedelta,
        timedelta_frequency=timedelta_frequency,
        state="closed",
    )
    return JSONResponse({"task_id": task.id})


@app.post("/contributorgrowth")
async def contributor_growth(
    request: Request,
    github_api: str,
    accesstoken: str = Cookie(None),
    timedelta: int = 7,
    timedelta_frequency: int = 2,
):
    task = contributorgrowth.delay(
        github_api=github_api,
        access_token=accesstoken,
        timedelta=timedelta,
        timedelta_frequency=timedelta_frequency,
    )
    return JSONResponse({"task_id": task.id})


def callback_helper(response: Response, gh_response):
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
        secure=True,
        samesite="strict",
    )
    response.set_cookie(
        key="refreshtoken",
        value="hello",
        httponly=True,
        expires=refresh_token_expires_in,
        secure=True,
        samesite="strict",
    )

    print(access_token)

    html_content = """
    <html>
        <body>
            <h1>You may now close this window.</h1>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


@app.get("/callback")
def callback(request: Request, code: str, response: Response):
    print(code)
    # gh_response = requests.post(
    #     "https://github.com/login/oauth/access_token",
    #     params={
    #         "code": code,
    #         "client_id": os.getenv("GITHUB_CLIENT_ID"),
    #         "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
    #     },
    # )
    # pattern = r"access_token=([\w-]+)&expires_in=(\d+)&refresh_token=([\w-]+)&refresh_token_expires_in=(\d+)"

    # match = re.search(pattern, gh_response.text)

    # if match:
    #     access_token = match.group(1)
    #     expires_in = int(match.group(2))
    #     refresh_token = match.group(3)
    #     refresh_token_expires_in = int(match.group(4))
    # else:
    #     return "API response isn't as expected."

    # response.set_cookie(
    #     key="accesstoken",
    #     value=access_token,
    #     httponly=True,
    #     # expires=expires_in,
    #     # secure=True,
    #     # samesite="strict",
    # )
    # response.set_cookie(
    #     key="refreshtoken",
    #     value=refresh_token,
    #     httponly=True,
    #     # expires=refresh_token_expires_in,
    #     # secure=True,
    #     # samesite="strict",
    # )

    # print(access_token)
    # print(refresh_token)

    # html_content = """
    # <html>
    #     <body>
    #         <h1>You may now close this window.</h1>
    #     </body>
    # </html>
    # """
    # return HTMLResponse(content=html_content, status_code=200)
    # # return callback_helper(response=response, gh_response=gh_response)


@app.get("/githubrefreshtoken")
def github_refresh_token(
    request: Request, response: Response, refresh_token: str = Cookie(None)
):
    gh_response = requests.post(
        "https://github.com/login/oauth/access_token",
        params={
            "grant_type": "refresh_token",
            "client_id": os.getenv("GITHUB_CLIENT_ID"),
            "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
            "refresh_token": refresh_token,
        },
    )
    return callback_helper(response=response, gh_response=gh_response)
