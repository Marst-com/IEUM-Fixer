import ast
import json
import subprocess
import shutil
from pathlib import Path


class Validator:

    def validate_file(self, path: Path):
        ext = path.suffix.lower()

        try:
            code = path.read_text(encoding="utf-8")
        except Exception as error:
            return {
                "valid": False,
                "error": str(error)
            }

        if ext == ".py":
            try:
                compile(code, str(path), "exec")
                return {"valid": True}
            except SyntaxError as error:
                return {
                    "valid": False,
                    "error": error.msg,
                    "line": error.lineno
                }

        if ext == ".json":
            try:
                json.loads(code)
                return {"valid": True}
            except json.JSONDecodeError as error:
                return {
                    "valid": False,
                    "error": error.msg,
                    "line": error.lineno
                }

        if ext in {".js", ".mjs", ".cjs"}:
            node = shutil.which("node")

            if not node:
                return {
                    "valid": None,
                    "message": "Node.js가 설치되지 않아 검증하지 못했습니다."
                }

            try:
                result = subprocess.run(
                    [node, "--check", str(path)],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    shell=False
                )

                return {
                    "valid": result.returncode == 0,
                    "error": result.stderr.strip() or None
                }

            except subprocess.TimeoutExpired:
                return {
                    "valid": None,
                    "message": "검증 시간이 초과되었습니다."
                }

        return {
            "valid": None,
            "message": "지원하지 않는 검증 형식입니다."
        }

    def validate_project(self, project_dir):
        results = []

        for path in project_dir.rglob("*"):
            if not path.is_file():
                continue

            if path.suffix.lower() not in {
                ".py", ".js", ".mjs", ".cjs", ".json"
            }:
                continue

            results.append({
                "path": path.relative_to(project_dir).as_posix(),
                **self.validate_file(path)
            })

        return results
