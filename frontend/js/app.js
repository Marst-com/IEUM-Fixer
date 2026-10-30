const App = {
    init() {
        Upload.init();
        Editor.init();

        document.getElementById("analyze").onclick =
            () => this.analyze();

        document.getElementById("saveFile").onclick =
            () => Editor.save();

        document.getElementById("repairAll").onclick =
            () => this.repairAll();

        document.getElementById("download").onclick =
            () => this.download();

        document.getElementById("newProject").onclick =
            () => this.newProject();

        this.checkServer();
    },

    async checkServer() {
        const status = document.getElementById("serverStatus");

        try {
            const result = await API.health();

            status.innerHTML = "";

            const dot = document.createElement("i");
            const label = document.createElement("span");

            dot.className = "online";
            label.textContent = result.ai.available
                ? "서버 연결됨 · PyTorch 모델 사용 가능"
                : "서버 연결됨 · 규칙 기반 분석";

            status.append(dot, label);

        } catch {
            status.textContent = "서버 연결 실패";
            status.classList.add("offline");
        }
    },

    openWorkspace(project) {
        document.getElementById("uploadPage").classList.add("hidden");
        document.getElementById("workspace").classList.remove("hidden");

        document.getElementById("projectName").textContent =
            project.project_id.slice(0, 12).toUpperCase();

        document.getElementById("projectStatus").textContent =
            `${project.file_count} files loaded`;

        Renderer.renderTree(project);

        const first = project.files[0];

        if (first) {
            Editor.open(first.path);
        }
    },

    async analyze() {
        try {
            if (!await Editor.saveBeforeAction()) return;

            const button = document.getElementById("analyze");

            button.disabled = true;
            button.textContent = "분석 중...";

            const result = await API.analyze();

            Renderer.renderIssues(result);

            document.getElementById("projectStatus").textContent =
                `Analysis completed · ${result.total} issues`;

        } catch (error) {
            alert("분석 실패: " + error.message);
        } finally {
            const button = document.getElementById("analyze");
            button.disabled = false;
            button.textContent = "분석 시작";
        }
    },

    async repairAll() {
        if (!confirm("안전한 자동 수정 규칙이 적용된 오류를 수정할까요?")) {
            return;
        }

        try {
            if (!await Editor.saveBeforeAction()) return;

            const result = await API.repairAll();

            alert(
                `${result.repaired_count}개 수정 완료\n` +
                `${result.skipped_count}개 수정 보류`
            );

            await this.analyze();

            if (Editor.currentPath) {
                await Editor.open(Editor.currentPath);
            }

        } catch (error) {
            alert("수정 실패: " + error.message);
        }
    },

    async download() {
        try {
            if (!await Editor.saveBeforeAction()) return;

            const validation = await API.validate();

            if (validation.invalid > 0) {
                const proceed = confirm(
                    `${validation.invalid}개의 파일에서 검증 오류가 발견되었습니다.\n` +
                    "그래도 ZIP을 다운로드할까요?"
                );

                if (!proceed) return;
            }

            await API.download();

        } catch (error) {
            alert("다운로드 실패: " + error.message);
        }
    },

    async newProject() {
        if (!confirm("현재 작업을 종료할까요?")) return;

        API.projectId = null;
        Editor.currentPath = null;
        Editor.modified = false;

        document.getElementById("workspace").classList.add("hidden");
        document.getElementById("uploadPage").classList.remove("hidden");

        document.getElementById("codeEditor").value = "";
        document.getElementById("issueList").innerHTML = "";

        document.getElementById("uploadMessage").textContent = "";
        document.getElementById("projectStatus").textContent = "No project";
    }
};

document.addEventListener("DOMContentLoaded", () => {
    App.init();
});
