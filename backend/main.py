from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
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


@app.get("/stargrowth")
def star_growth(
    github_api: str,
    timedelta: int = 7,
    timedelta_frequency: int = 2,
    authorization: str = Header(default=None),
):
    scheme, accesstoken = authorization.split()
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")
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
    timedelta: int = 7,
    timedelta_frequency: int = 2,
    issue_stats: bool = False,
    authorization: str = Header(default=None),
):
    scheme, accesstoken = authorization.split()
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")
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
    timedelta: int = 7,
    timedelta_frequency: int = 2,
    authorization: str = Header(default=None),
):
    scheme, accesstoken = authorization.split()
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")
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
    timedelta: int = 7,
    timedelta_frequency: int = 2,
    authorization: str = Header(default=None),
):
    scheme, accesstoken = authorization.split()
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")

    task = contributorgrowth.delay(
        github_api=github_api,
        access_token=accesstoken,
        timedelta=timedelta,
        timedelta_frequency=timedelta_frequency,
    )
    return JSONResponse({"task_id": task.id})
