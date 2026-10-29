
const Analyzer = {
    analyze() {
        const issues = [];

        for (const [path, file] of Project.files) {
            const ext = path.split(".").pop().toLowerCase();

            if (ext === "js" || ext === "mjs" || ext === "cjs") {
                issues.push(...this.analyzeJavaScript(path, file.content));
            }

            if (ext === "css") {
                issues.push(...this.analyzeCSS(path, file.content));
            }

            if (ext === "html" || ext === "htm") {
                issues.push(...this.analyzeHTML(path, file.content));
            }

            if (ext === "json") {
                issues.push(...this.analyzeJSON(path, file.content));
            }
        }

        Project.issues = issues;
        return issues;
    },

    analyzeJavaScript(path, code) {
        const issues = [];

        try {
            new Function(code);
        } catch (error) {
            const match = error.stack?.match(/<anonymous>:(\d+):(\d+)/);
            issues.push({
                id: crypto.randomUUID(),
                path,
                type: "error",
                title: "JavaScript Syntax Error",
                message: error.message,
                line: match ? Number(match[1]) : 1,
                fixable: false
            });
        }

        const lines = code.split("\n");

        lines.forEach((line, index) => {
            const trimmed = line.trim();

            if (!trimmed || trimmed.startsWith("//")) return;

            if (/\bconsole\.log\s*\(\s*\)/.test(line)) {
                issues.push({
                    id: crypto.randomUUID(),
                    path,
                    type: "warning",
                    title: "Empty console.log",
                    message: "출력할 값이 없는 console.log입니다.",
                    line: index + 1,
                    fixable: false
                });
            }

            const typo = trimmed.match(/\b(?:funktion|functon|funtion|funciton)\b/);

            if (typo) {
                issues.push({
                    id: crypto.randomUUID(),
                    path,
                    type: "warning",
                    title: "Possible Typo",
                    message: `"${typo[0]}"가 오타일 수 있습니다.`,
                    line: index + 1,
                    fixable: true,
                    replacement: "function"
                });
            }
        });

        return issues;
    },

    analyzeCSS(path, code) {
        const issues = [];
        let braces = 0;

        for (let i = 0; i < code.length; i++) {
            if (code[i] === "{") braces++;
            if (code[i] === "}") braces--;

            if (braces < 0) {
                issues.push({
                    id: crypto.randomUUID(),
                    path,
                    type: "error",
                    title: "Unexpected CSS Brace",
                    message: "열린 중괄호 없이 닫는 중괄호가 있습니다.",
                    line: code.slice(0, i).split("\n").length,
                    fixable: false
                });

                braces = 0;
            }
        }

        if (braces > 0) {
            issues.push({
                id: crypto.randomUUID(),
                path,
                type: "error",
                title: "Unclosed CSS Block",
                message: "닫히지 않은 CSS 중괄호가 있습니다.",
                line: code.split("\n").length,
                fixable: false
            });
        }

        return issues;
    },

    analyzeHTML(path, code) {
        const issues = [];

        const tags = [...code.matchAll(/<\/?([a-z][\w-]*)\b[^>]*>/gi)];
        const stack = [];
        const voidTags = new Set([
            "area", "base", "br", "col", "embed", "hr",
            "img", "input", "link", "meta", "param",
            "source", "track", "wbr"
        ]);

        for (const match of tags) {
            const tag = match[1].toLowerCase();
            const closing = match[0].startsWith("</");
            const selfClosing = /\/>$/.test(match[0]);

            if (voidTags.has(tag) || selfClosing) continue;

            if (!closing) {
                stack.push({ tag, index: match.index });
                continue;
            }

            if (stack.length && stack[stack.length - 1].tag === tag) {
                stack.pop();
            } else {
                issues.push({
                    id: crypto.randomUUID(),
                    path,
                    type: "warning",
                    title: "HTML Tag Mismatch",
                    message: `닫는 태그 </${tag}>의 위치가 올바르지 않을 수 있습니다.`,
                    line: code.slice(0, match.index).split("\n").length,
                    fixable: false
                });
            }
        }

        for (const item of stack) {
            issues.push({
                id: crypto.randomUUID(),
                path,
                type: "warning",
                title: "Unclosed HTML Tag",
                message: `<${item.tag}> 태그가 닫히지 않았습니다.`,
                line: code.slice(0, item.index).split("\n").length,
                fixable: false
            });
        }

        return issues;
    },

    analyzeJSON(path, code) {
        try {
            JSON.parse(code);
            return [];
        } catch (error) {
            return [{
                id: crypto.randomUUID(),
                path,
                type: "error",
                title: "Invalid JSON",
                message: error.message,
                line: Number(error.message.match(/position\s+(\d+)/i)?.[1] || 0),
                fixable: false
            }];
        }
    }
};
