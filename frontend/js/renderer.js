const Renderer = {
    renderTree(project) {
        const tree = document.getElementById("fileTree");
        tree.innerHTML = "";

        for (const file of project.files) {
            const item = document.createElement("button");

            item.className = "file-item";
            item.type = "button";

            const icon = this.getIcon(file.extension);

            const iconElement = document.createElement("span");
            iconElement.textContent = icon;

            const nameElement = document.createElement("span");
            nameElement.textContent = file.path;

            item.append(iconElement, nameElement);

            if (Editor.currentPath === file.path) {
                item.classList.add("active");
            }

            item.addEventListener("click", () => {
                Editor.open(file.path);
            });

            tree.appendChild(item);
        }
    },

    getIcon(extension) {
        const icons = {
            ".js": "JS",
            ".mjs": "JS",
            ".py": "PY",
            ".html": "HT",
            ".css": "CS",
            ".json": "JN",
            ".md": "MD"
        };

        return icons[extension] || "◇";
    },

    renderIssues(result) {
        const list = document.getElementById("issueList");
        list.innerHTML = "";

        document.getElementById("errors").textContent = result.errors;
        document.getElementById("warnings").textContent = result.warnings;

        document.getElementById("issueCount").textContent =
            `${result.total} Issues`;

        if (!result.issues.length) {
            const empty = document.createElement("div");
            empty.className = "empty";
            empty.textContent = "발견된 오류가 없습니다.";
            list.appendChild(empty);
            return;
        }

        for (const issue of result.issues) {
            const card = document.createElement("div");
            card.className = "issue-card";

            const title = document.createElement("strong");
            title.textContent =
                `${issue.severity === "error" ? "🔴" : "🟡"} ${issue.title}`;

            const message = document.createElement("p");
            message.textContent = issue.message;

            const meta = document.createElement("small");
            meta.textContent = `${issue.path} · ${issue.line}행`;

            card.append(title, message, meta);

            card.addEventListener("click", () => {
                Editor.open(issue.path);
            });

            if (issue.ai?.available) {
                const ai = document.createElement("small");
                ai.className = "ai-result";

                ai.textContent =
                    `AI: ${issue.ai.category} · ${(issue.ai.confidence * 100).toFixed(1)}%`;

                card.appendChild(ai);
            }

            list.appendChild(card);
        }
    }
};
