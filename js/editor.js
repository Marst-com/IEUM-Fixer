
const Editor = {
    init() {
        const textarea = document.getElementById("codeEditor");

        textarea.addEventListener("input", () => {
            if (!Project.currentFile) return;

            Project.updateFile(
                Project.currentFile,
                textarea.value
            );

            this.updateFileTree();
        });

        textarea.addEventListener("keydown", e => {
            if (e.key === "Tab") {
                e.preventDefault();

                const start = textarea.selectionStart;
                const end = textarea.selectionEnd;

                textarea.setRangeText(
                    "    ",
                    start,
                    end,
                    "end"
                );

                textarea.dispatchEvent(new Event("input"));
            }
        });
    },

    openFile(path) {
        const file = Project.getFile(path);
        if (!file) return;

        Project.currentFile = path;

        document.getElementById("currentFile").textContent = path;
        document.getElementById("codeEditor").value = file.content;

        const ext = path.split(".").pop().toUpperCase();
        document.getElementById("fileLanguage").textContent = ext;

        this.updateFileTree();
    },

    updateFileTree() {
        const tree = document.getElementById("fileTree");
        tree.innerHTML = "";

        const paths = [...Project.files.keys()].sort();

        for (const path of paths) {
            const file = Project.getFile(path);
            const item = document.createElement("div");

            item.className = "file-item" +
                (Project.currentFile === path ? " active" : "");

            const icon = file.modified ? "●" : "◇";
            item.textContent = `${icon} ${path}`;
            item.title = path;

            item.addEventListener("click", () => {
                this.openFile(path);
            });

            tree.appendChild(item);
        }
    },

    renderIssues() {
        const issues = Project.issues;
        const list = document.getElementById("issueList");

        list.innerHTML = "";

        const errors = issues.filter(i => i.type === "error").length;
        const warnings = issues.filter(i => i.type === "warning").length;

        document.getElementById("errorCount").textContent = errors;
        document.getElementById("warningCount").textContent = warnings;
        document.getElementById("issueCount").textContent =
            `${issues.length} Issues`;

        if (!issues.length) {
            list.innerHTML = `
                <div class="empty-state">
                    <span>✓</span>
                    <p>발견된 오류가 없습니다.</p>
                </div>`;
            return;
        }

        for (const issue of issues) {
            const element = document.createElement("div");
            element.className = "issue";

            const title = document.createElement("div");
            title.className = "issue-title";
            title.textContent = `${issue.type === "error" ? "🔴" : "🟡"} ${issue.title}`;

            const description = document.createElement("div");
            description.className = "issue-description";
            description.textContent = issue.message;

            const meta = document.createElement("div");
            meta.className = "issue-meta";
            meta.textContent = `${issue.path} : ${issue.line}`;

            element.append(title, description, meta);

            element.addEventListener("click", () => {
                this.openFile(issue.path);
            });

            list.appendChild(element);
        }
    }
};
