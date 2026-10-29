import zipfile
import uuid
import shutil
from pathlib import Path, PurePosixPath

from config import (
    PROJECTS_DIR,
    MAX_UPLOAD_SIZE,
    MAX_EXTRACTED_SIZE,
    MAX_FILES
)


class ProjectLoader:

    @staticmethod
    def create_project():
        project_id = uuid.uuid4().hex
        project_dir = PROJECTS_DIR / project_id
        project_dir.mkdir(parents=True)

        return project_id, project_dir

    @staticmethod
    def safe_path(root: Path, name: str):
        normalized = name.replace("\\", "/")
        path = PurePosixPath(normalized)

        if path.is_absolute() or ".." in path.parts:
            raise ValueError("Invalid archive path")

        if not path.parts:
            raise ValueError("Empty archive path")

        destination = (root / Path(*path.parts)).resolve()

        if not destination.is_relative_to(root.resolve()):
            raise ValueError("Path traversal detected")

        return destination

    @classmethod
    def extract_zip(cls, archive: Path, destination: Path):
        total_size = 0
        count = 0

        with zipfile.ZipFile(archive) as zf:
            for info in zf.infolist():

                if info.is_dir():
                    continue

                count += 1
                total_size += info.file_size

                if count > MAX_FILES:
                    raise ValueError("Too many files")

                if total_size > MAX_EXTRACTED_SIZE:
                    raise ValueError("Extracted project too large")

                if info.file_size > 50 * 1024 * 1024:
                    raise ValueError("Individual file too large")

                mode = (info.external_attr >> 16) & 0o170000

                if mode == 0o120000:
                    raise ValueError("Symbolic links are not allowed")

                target = cls.safe_path(destination, info.filename)
                target.parent.mkdir(parents=True, exist_ok=True)

                with zf.open(info) as source, target.open("wb") as output:
                    shutil.copyfileobj(source, output)

        return count

    @staticmethod
    def list_files(project_dir: Path):
        result = []

        for path in project_dir.rglob("*"):
            if not path.is_file():
                continue

            relative = path.relative_to(project_dir).as_posix()

            if any(part.startswith(".") and part in {
                ".git", ".idea", ".vscode", "__pycache__"
            } for part in Path(relative).parts):
                continue

            result.append({
                "path": relative,
                "size": path.stat().st_size,
                "extension": path.suffix.lower()
            })

        return sorted(result, key=lambda x: x["path"])

    @staticmethod
    def read_file(project_dir: Path, relative_path: str):
        target = ProjectLoader.safe_path(project_dir, relative_path)

        if not target.is_file():
            raise FileNotFoundError(relative_path)

        if target.stat().st_size > 5 * 1024 * 1024:
            raise ValueError("File too large to edit")

        return target.read_text(encoding="utf-8", errors="replace")

    @staticmethod
    def write_file(project_dir: Path, relative_path: str, content: str):
        target = ProjectLoader.safe_path(project_dir, relative_path)

        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    @staticmethod
    def get_project(project_id: str):
        if not project_id.isalnum() or len(project_id) != 32:
            raise ValueError("Invalid project ID")

        directory = PROJECTS_DIR / project_id

        if not directory.is_dir():
            raise FileNotFoundError(project_id)

        return directory
