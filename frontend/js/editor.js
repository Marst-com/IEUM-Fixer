const Editor = {
    currentPath: null,
    modified: false,

    init() {
        const textarea = document.getElementById("codeEditor");

        textarea.addEventListener("input", () => {
            this.modified = true;
            document.getElementById("fileInfo").textContent =
                "● 수정됨";
        });

        textarea.addEventListener("keydown", e => {
            if (e.key === "Tab") {
                e.preventDefault();

                const start = textarea.selectionStart;
                const end = textarea.selectionEnd;

                textarea.setRangeText("    ", start, end, "end");
            }

            if ((e.ctrlKey || e.metaKey) && e.key === "s") {
                e.preventDefault();
                this.save();
            }
        });
    },

    async open(path) {
        if (this.modified) {
            const save = confirm("변경사항을 저장할까요?");

            if (save) {
                await this.save();
            }
        }

        try {
            const result = await API.getFile(path);

            this.currentPath = path;
            this.modified = false;

            const editor = document.getElementById("codeEditor");

            editor.value = result.content;

            document.getElementById("currentFile").textContent = path;
            document.getElementById("language").textContent =
                path.split(".").pop().toUpperCase();

            document.getElementById("fileInfo").textContent = "저장됨";

            Renderer.renderTree(
                await API.getProject()
            );

        } catch (error) {
            alert("파일 열기 실패: " + error.message);
        }
    },

    async save() {
        if (!this.currentPath) return;

        try {
            await API.saveFile(
                this.currentPath,
                document.getElementById("codeEditor").value
            );

            this.modified = false;

            document.getElementById("fileInfo").textContent = "저장됨";

            return true;
        } catch (error) {
            alert("저장 실패: " + error.message);
            return false;
        }
    },

    async saveBeforeAction() {
        if (this.modified) {
            return await this.save();
        }

        return true;
    }
};
