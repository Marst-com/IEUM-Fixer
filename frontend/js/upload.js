const Upload = {
    init() {
        const drop = document.getElementById("dropZone");
        const zipInput = document.getElementById("zipInput");
        const folderInput = document.getElementById("folderInput");

        document.getElementById("selectZip").onclick =
            () => zipInput.click();

        document.getElementById("selectFolder").onclick =
            () => folderInput.click();

        zipInput.addEventListener("change", async e => {
            if (e.target.files[0]) {
                await this.handleZip(e.target.files[0]);
            }

            e.target.value = "";
        });

        folderInput.addEventListener("change", async e => {
            if (e.target.files.length) {
                await this.handleFolder(e.target.files);
            }

            e.target.value = "";
        });

        drop.addEventListener("dragover", e => {
            e.preventDefault();
            drop.classList.add("dragover");
        });

        drop.addEventListener("dragleave", () => {
            drop.classList.remove("dragover");
        });

        drop.addEventListener("drop", async e => {
            e.preventDefault();
            drop.classList.remove("dragover");

            const files = [...e.dataTransfer.files];

            if (files.length === 1 &&
                files[0].name.toLowerCase().endsWith(".zip")) {
                await this.handleZip(files[0]);
            } else {
                await this.handleFolder(files);
            }
        });
    },

    async handleFolder(files) {
        try {
            const zip = new JSZip();

            for (const file of files) {
                const path = file.webkitRelativePath || file.name;

                if (
                    path.split("/").some(part =>
                        ["node_modules", ".git", "__pycache__", ".venv"]
                            .includes(part)
                    )
                ) {
                    continue;
                }

                zip.file(path, file);
            }

            const blob = await zip.generateAsync({
                type: "blob",
                compression: "DEFLATE",
                compressionOptions: { level: 4 }
            });

            const archive = new File(
                [blob],
                "project.zip",
                { type: "application/zip" }
            );

            await this.handleZip(archive);

        } catch (error) {
            alert("폴더 압축 오류: " + error.message);
        }
    },

    async handleZip(file) {
        const progress = document.getElementById("uploadProgress");
        const message = document.getElementById("uploadMessage");

        try {
            if (file.size > 100 * 1024 * 1024) {
                throw new Error("ZIP 파일은 100MB 이하여야 합니다.");
            }

            progress.classList.remove("hidden");
            message.textContent = "프로젝트 업로드 중...";

            document.getElementById("progressBar").style.width = "50%";

            const result = await API.upload(file);

            document.getElementById("progressBar").style.width = "100%";

            message.textContent =
                `${result.file_count}개 파일 업로드 완료`;

            App.openWorkspace(result);

        } catch (error) {
            message.textContent = "업로드 실패: " + error.message;
        } finally {
            setTimeout(() => progress.classList.add("hidden"), 800);
        }
    }
};
