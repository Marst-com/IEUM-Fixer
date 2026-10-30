import os
import uuid
import shutil
import tempfile
import zipfile

from pathlib import Path
from collections import defaultdict

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from config import (
    PROJECTS_DIR,
    MAX_UPLOAD_SIZE,
    ALLOWED_ORIGINS
)

from engine.project_loader import ProjectLoader
from engine.analyzer import Analyzer
from engine.repair_engine import RepairEngine
from engine.validator import Validator
from ai.inference import InferenceEngine


app = FastAPI(
    title="IEUM Fixer API",
    version="0.2.0",
    description="AI-Powered Project Recovery System"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"]
)


analyzer = Analyzer()
repair_engine = RepairEngine()
validator = Validator()
inference = InferenceEngine()

PROJECT_ISSUES = defaultdict(list)
PROJECT_REPAIRS = defaultdict(list)


class FileUpdate(BaseModel):
    path: str = Field(min_length=1, max_length=500)
    content: str = Field(max_length=5_000_000)


class RepairRequest(BaseModel):
    issue_id: str


def get_project(project_id):
    try:
        return ProjectLoader.get_project(project_id)
    except (ValueError, FileNotFoundError):
        raise HTTPException(404, "Project not found")


@app.get("/")
def root():
    return {
        "name": "IEUM Fixer",
        "version": "0.2.0",
        "status": "online"
    }


@app.get("/api/health")
def health():
    return {
        "status": "online",
        "ai": {
            "available": inference.ai.available,
            "engine": "PyTorch"
        }
    }


@app.post("/api/projects/upload")
async def upload_project(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".zip"):
        raise HTTPException(400, "ZIP 파일만 업로드할 수 있습니다.")

    project_id, project_dir = ProjectLoader.create_project()

    temp_path = None

    try:
        size = 0

        with tempfile.NamedTemporaryFile(
            suffix=".zip",
            delete=False
        ) as temp:
            temp_path = Path(temp.name)

            while True:
                chunk = await file.read(1024 * 1024)

                if not chunk:
                    break

                size += len(chunk)

                if size > MAX_UPLOAD_SIZE:
                    raise HTTPException(413, "업로드 용량이 초과되었습니다.")

                temp.write(chunk)

        if not zipfile.is_zipfile(temp_path):
            raise HTTPException(400, "올바른 ZIP 파일이 아닙니다.")

        count = ProjectLoader.extract_zip(
            temp_path,
            project_dir
        )

        if count == 0:
            raise HTTPException(400, "프로젝트에 파일이 없습니다.")

        return {
            "success": True,
            "project_id": project_id,
            "file_count": count,
            "files": ProjectLoader.list_files(project_dir)
        }

    except HTTPException:
        shutil.rmtree(project_dir, ignore_errors=True)
        raise

    except Exception as error:
        shutil.rmtree(project_dir, ignore_errors=True)
        raise HTTPException(400, str(error))

    finally:
        await file.close()

        if temp_path and temp_path.exists():
            temp_path.unlink(missing_ok=True)


@app.get("/api/projects/{project_id}")
def get_project_info(project_id: str):
    project_dir = get_project(project_id)

    return {
        "project_id": project_id,
        "files": ProjectLoader.list_files(project_dir)
    }


@app.get("/api/projects/{project_id}/file")
def get_file(project_id: str, path: str):
    project_dir = get_project(project_id)

    try:
        content = ProjectLoader.read_file(project_dir, path)

        return {
            "path": path,
            "content": content
        }

    except (ValueError, FileNotFoundError) as error:
        raise HTTPException(400, str(error))


@app.put("/api/projects/{project_id}/file")
def update_file(project_id: str, data: FileUpdate):
    project_dir = get_project(project_id)

    try:
        ProjectLoader.write_file(
            project_dir,
            data.path,
            data.content
        )

        return {"success": True}

    except (ValueError, OSError) as error:
        raise HTTPException(400, str(error))


@app.post("/api/projects/{project_id}/analyze")
def analyze_project(project_id: str):
    project_dir = get_project(project_id)

    issues = analyzer.analyze_project(project_dir)

    for issue in issues:
        issue["ai"] = inference.classify(issue)

    PROJECT_ISSUES[project_id] = issues

    errors = sum(
        1 for item in issues
        if item["severity"] == "error"
    )

    warnings = sum(
        1 for item in issues
        if item["severity"] == "warning"
    )

    return {
        "success": True,
        "total": len(issues),
        "errors": errors,
        "warnings": warnings,
        "issues": issues
    }


@app.post("/api/projects/{project_id}/repair")
def repair_project(project_id: str, data: RepairRequest):
    project_dir = get_project(project_id)

    issue = next(
        (
            item for item in PROJECT_ISSUES[project_id]
            if item["id"] == data.issue_id
        ),
        None
    )

    if not issue:
        raise HTTPException(404, "Issue not found")

    result = repair_engine.repair(
        project_dir,
        issue
    )

    if result["success"]:
        PROJECT_REPAIRS[project_id].append(
            result["repair_id"]
        )

        return {
            **result,
            "validation": validator.validate_project(project_dir)
        }

    return result


@app.post("/api/projects/{project_id}/repair/safe-all")
def repair_all(project_id: str):
    project_dir = get_project(project_id)

    repaired = []
    skipped = []

    for issue in list(PROJECT_ISSUES[project_id]):
        result = repair_engine.repair(
            project_dir,
            issue
        )

        if result["success"]:
            repaired.append(result)
            PROJECT_REPAIRS[project_id].append(
                result["repair_id"]
            )
        else:
            skipped.append({
                "issue_id": issue["id"],
                "reason": result["reason"]
            })

    validation = validator.validate_project(project_dir)

    return {
        "success": True,
        "repaired_count": len(repaired),
        "skipped_count": len(skipped),
        "repaired": repaired,
        "skipped": skipped,
        "validation": validation
    }


@app.post("/api/projects/{project_id}/validate")
def validate_project(project_id: str):
    project_dir = get_project(project_id)

    results = validator.validate_project(project_dir)

    valid = sum(1 for item in results if item.get("valid") is True)
    invalid = sum(1 for item in results if item.get("valid") is False)
    unknown = sum(1 for item in results if item.get("valid") is None)

    return {
        "total": len(results),
        "valid": valid,
        "invalid": invalid,
        "unknown": unknown,
        "results": results
    }


@app.get("/api/projects/{project_id}/download")
def download_project(project_id: str):
    project_dir = get_project(project_id)

    archive = PROJECTS_DIR / f"{project_id}-fixed.zip"

    with zipfile.ZipFile(
        archive,
        "w",
        compression=zipfile.ZIP_DEFLATED
    ) as zf:

        for path in project_dir.rglob("*"):
            if path.is_file():
                zf.write(
                    path,
                    path.relative_to(project_dir).as_posix()
                )

    return FileResponse(
        archive,
        media_type="application/zip",
        filename="IEUM-Fixer-Recovered.zip",
        background=None
    )


@app.get("/api/projects/{project_id}/issues")
def get_issues(project_id: str):
    get_project(project_id)

    return {
        "issues": PROJECT_ISSUES[project_id]
    }


@app.get("/api/projects/{project_id}/repairs")
def get_repairs(project_id: str):
    get_project(project_id)

    return {
        "repairs": PROJECT_REPAIRS[project_id]
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=True
    )
