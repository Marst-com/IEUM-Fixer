import re
import uuid
from pathlib import Path


class RepairEngine:

    TYPO_MAP = {
        "functon": "function",
        "funtion": "function",
        "funciton": "function",
        "funktion": "function"
    }

    def __init__(self):
        self.history = {}

    def repair(self, project_dir: Path, issue: dict):
        path = issue.get("path", "")
        title = issue.get("title", "")

        if title != "Possible Typo":
            return {
                "success": False,
                "reason": "안전한 자동 수정 규칙이 없습니다."
            }

        target = (project_dir / path).resolve()

        if not target.is_relative_to(project_dir.resolve()):
            return {
                "success": False,
                "reason": "잘못된 파일 경로입니다."
            }

        if not target.is_file():
            return {
                "success": False,
                "reason": "파일을 찾을 수 없습니다."
            }

        original = target.read_text(encoding="utf-8")
        lines = original.splitlines(keepends=True)

        line_number = issue.get("line", 1) - 1

        if line_number < 0 or line_number >= len(lines):
            return {
                "success": False,
                "reason": "오류 위치가 유효하지 않습니다."
            }

        line = lines[line_number]

        pattern = re.compile(
            r"\b(" + "|".join(map(re.escape, self.TYPO_MAP)) + r")\b"
        )

        match = pattern.search(line)

        if not match:
            return {
                "success": False,
                "reason": "수정할 오타를 찾지 못했습니다."
            }

        typo = match.group(1)
        replacement = self.TYPO_MAP[typo]

        # function 선언이나 호출의 의도가 불명확하므로
        # function 키워드가 아닌 식별자 위치만 수정한다.
        before = line[:match.start()]
        after = line[match.end():]

        if re.search(r"\b(?:function|typeof|new)\s*$", before):
            return {
                "success": False,
                "reason": "문맥이 불분명해 자동 수정을 보류했습니다."
            }

        if after.lstrip().startswith(":"):
            return {
                "success": False,
                "reason": "문맥이 불분명해 자동 수정을 보류했습니다."
            }

        new_line = (
            before + replacement + after
        )

        lines[line_number] = new_line
        updated = "".join(lines)

        repair_id = uuid.uuid4().hex

        self.history[repair_id] = {
            "path": str(target),
            "original": original,
            "updated": updated
        }

        target.write_text(updated, encoding="utf-8")

        return {
            "success": True,
            "repair_id": repair_id,
            "path": path,
            "before": original,
            "after": updated,
            "message": f"{typo} → {replacement}"
        }

    def rollback(self, repair_id):
        record = self.history.get(repair_id)

        if not record:
            return False

        target = Path(record["path"])
        target.write_text(
            record["original"],
            encoding="utf-8"
        )

        del self.history[repair_id]
        return True
