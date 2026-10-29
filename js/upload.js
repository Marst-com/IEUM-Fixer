
const Upload = {
    init() {
        const drop = document.getElementById("dropZone");
        const fileInput = document.getElementById("fileInput");
        const zipInput = document.getElementById("zipInput");

        document.getElementById("selectFiles").onclick =
            () => fileInput.click();

        document.getElementById("selectZip").onclick =
            () => zipInput.click();

        fileInput.addEventListener("change", e => {
            this.handleFiles(e.target.files);
            e.target.value = "";
        });

        zipInput.addEventListener("change", e => {
            this.handleFiles(e.target.files);
            e.target.value = "";
        });

        ["dragenter", "dragover"].forEach(event => {
            drop.addEventListener(event, e => {
                e.preventDefault();
                drop.classList.add("dragover");
            });
        });

        ["dragleave", "drop"].forEach(event => {
            drop.addEventListener(event, e => {
                e.preventDefault();
                drop.classList.remove("dragover");
            });
        });

        drop.addEventListener("drop", e => {
            this.handleFiles(e.dataTransfer.files);
        });
    },

    async handleFiles(fileList) {
        const files = [...fileList];

        if (!files.length) return;

        Project.clear();

        const zipFiles = files.filter(f =>
            f.name.toLowerCase().endsWith(".zip")
        );

        const normalFiles = files.filter(f =>
            !f.name.toLowerCase().endsWith(".zip")
        );

        if (zipFiles.length && normalFiles.length) {
            alert("ZIP 파일과 일반 파일은 한 번에 섞어 업로드할 수 없습니다.");
            return;
        }

        if (zipFiles.length) {
            if (zipFiles.length !== 1) {
                alert("ZIP 파일은 한 번에 하나씩 업로드해 주세요.");
                return;
            }

            await ZipManager.extract(zipFiles[0]);
        } else {
            for (const file of normalFiles) {
                Project.addFile(file.webkitRelativePath || file.name,
                    await file.text());
            }
        }

        if (!Project.getFileCount()) {
            alert("업로드할 수 있는 파일이 없습니다.");
            return;
        }

        Project.name = zipFiles[0]?.name.replace(/\.zip$/i, "") ||
            "Uploaded Project";

        App.openWorkspace();
    }
};
