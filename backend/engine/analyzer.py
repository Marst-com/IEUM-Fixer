import ast
import json
import re
import uuid
from html.parser import HTMLParser


def make_issue(path, title, message, line, severity="error",
               fixable=False, replacement=None):
    return {
        "id": uuid.uuid4().hex,
        "path": path,
        "title": title,
        "message": message,
        "line": max(1, line),
        "severity": severity,
        "fixable": fixable,
        "replacement": replacement
    }


class HTMLChecker(HTMLParser):

    VOID_TAGS = {
        "area", "base", "br", "col", "embed", "hr",
        "img", "input", "link", "meta", "param",
        "source", "track", "wbr"
    }

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.issues = []

    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID_TAGS:
            self.stack.append((tag, self.getpos()[0]))

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        if tag in self.VOID_TAGS:
            return

        if not self.stack:
            self.issues.append(make_issue(
                "",
                "Unexpected HTML Closing Tag",
                f"닫을 태그가 없는 </{tag}> 태그입니다.",
                self.getpos()[0],
                "warning"
            ))
            return

        if self.stack[-1][0] == tag:
            self.stack.pop()
            return

        found = next(
            (i for i in range(len(self.stack) - 1, -1, -1)
             if self.stack[i][0] == tag),
            -1
        )

        if found == -1:
            self.issues.append(make_issue(
                "",
                "Unexpected HTML Closing Tag",
                f"열리지 않은 </{tag}> 태그입니다.",
                self.getpos()[0],
                "warning"
            ))
        else:
            self.issues.append(make_issue(
                "",
                "HTML Tag Mismatch",
                f"<{self.stack[-1][0]}> 태그가 먼저 닫혀야 합니다.",
                self.getpos()[0],
                "warning"
            ))
            self.stack = self.stack[:found]

    def finish(self):
        for tag, line in self.stack:
            self.issues.append(make_issue(
                "",
                "Unclosed HTML Tag",
                f"<{tag}> 태그가 닫히지 않았습니다.",
                line,
                "warning"
            ))

        return self.issues


class Analyzer:

    MAX_ANALYZE_SIZE = 2 * 1024 * 1024

    def analyze_project(self, project_dir):
        issues = []

        ignored = {
            "node_modules",
            ".git",
            "__pycache__",
            "dist",
            "build",
            ".venv",
            "venv"
        }

        for path in project_dir.rglob("*"):
            if not path.is_file():
                continue

            relative = path.relative_to(project_dir)

            if any(part in ignored for part in relative.parts):
                continue

            if path.stat().st_size > self.MAX_ANALYZE_SIZE:
                continue

            try:
                code = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue

            ext = path.suffix.lower()

            if ext == ".py":
                found = self.analyze_python(code, relative.as_posix())

            elif ext in {".js", ".mjs", ".cjs"}:
                found = self.analyze_javascript(code, relative.as_posix())

            elif ext in {".html", ".htm"}:
                found = self.analyze_html(code, relative.as_posix())

            elif ext == ".css":
                found = self.analyze_css(code, relative.as_posix())

            elif ext in {".json", ".jsonc"}:
                found = self.analyze_json(code, relative.as_posix())

            else:
                found = []

            issues.extend(found)

        return issues

    def analyze_python(self, code, path):
        issues = []

        try:
            ast.parse(code, filename=path)
        except SyntaxError as error:
            issues.append(make_issue(
                path,
                "Python Syntax Error",
                error.msg,
                error.lineno or 1,
                "error"
            ))

        return issues

    def analyze_javascript(self, code, path):
        issues = []

        lines = code.splitlines()

        # 기본적인 오타 후보 탐지.
        # 문맥이 불분명하므로 자동 수정은 하지 않는다.
        typo_patterns = [
            (r"\bfuncton\b", "function"),
            (r"\bfuntion\b", "function"),
            (r"\bfunciton\b", "function"),
            (r"\bfunktion\b", "function")
        ]

        for index, line in enumerate(lines, 1):
            stripped = line.strip()

            if not stripped or stripped.startswith("//"):
                continue

            for pattern, replacement in typo_patterns:
                match = re.search(pattern, line)

                if match:
                    issues.append(make_issue(
                        path,
                        "Possible Typo",
                        f"'{match.group()}'가 '{replacement}'의 오타일 수 있습니다.",
                        index,
                        "warning"
                    ))

            if re.search(r"\bdebugger\s*;", line):
                issues.append(make_issue(
                    path,
                    "Debugger Statement",
                    "배포 코드에 debugger 문이 남아 있습니다.",
                    index,
                    "warning"
                ))

        return issues

    def analyze_html(self, code, path):
        parser = HTMLChecker()

        try:
            parser.feed(code)
            parser.close()
            issues = parser.finish()

            for issue in issues:
                issue["path"] = path

            return issues

        except Exception as error:
            return [make_issue(
                path,
                "HTML Parsing Error",
                str(error),
                1
            )]

    def analyze_css(self, code, path):
        issues = []

        depth = 0
        quote = None
        escaped = False
        comment = False
        line = 1

        for char in code:
            if char == "\n":
                line += 1

            if comment:
                if char == "/":
                    comment = False
                continue

            if quote:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == quote:
                    quote = None
                continue

            if char in ("'", '"'):
                quote = char
                continue

            if char == "/" and len(code) > 1:
                # CSS 주석은 별도 간단 처리
                pass

            if char == "{":
                depth += 1

            elif char == "}":
                depth -= 1

                if depth < 0:
                    issues.append(make_issue(
                        path,
                        "Unexpected CSS Brace",
                        "열린 중괄호 없이 닫는 중괄호가 있습니다.",
                        line
                    ))
                    depth = 0

        if depth > 0:
            issues.append(make_issue(
                path,
                "Unclosed CSS Block",
                f"{depth}개의 CSS 블록이 닫히지 않았습니다.",
                line
            ))

        if quote:
            issues.append(make_issue(
                path,
                "Unclosed CSS String",
                "문자열의 따옴표가 닫히지 않았습니다.",
                line
            ))

        return issues

    def analyze_json(self, code, path):
        try:
            json.loads(code)
            return []

        except json.JSONDecodeError as error:
            return [make_issue(
                path,
                "Invalid JSON",
                error.msg,
                error.lineno
            )]
