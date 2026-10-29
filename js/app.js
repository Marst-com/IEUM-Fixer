
const App = {
    init() {
        Upload.init();
        Editor.init();

        document.getElementById("analyzeBtn").onclick =
            () => this.analyze();

        document.getElementById("repairAllBtn").onclick =
            () => this.repairAll();

        document.getElementById("downloadBtn").onclick =
            () => ZipManager.download();

        document.getElementById("newProject").onclick =
            () => this.newProject();

        document.getElementById("collapseTree").onclick = () => {
            const tree = document.getElementById("fileTree");
            tree.classList.toggle("hidden");
        };
    },

    openWorkspace() {
        document.getElementById("uploadView").classList.add("hidden");
        document.getElementById("workspace").classList.remove("hidden");

        document.getElementById("projectName").textContent =
            Project.name.toUpperCase();

        document.getElementById("projectStatus").textContent =
            `${Project.getFileCount()} files loaded`;

        Editor.updateFileTree();

        const firstFile = Project.files.keys().next().value;

        if (firstFile) {
            Editor.openFile(firstFile);
        }
    },

    analyze() {
        const issues = Analyzer.analyze();
        Editor.renderIssues();

        document.getElementById("projectStatus").textContent =
            `Analysis complete · ${issues.length} issues found`;
    },

    async repairAll() {
        const fixed = await Repair.fixAll();

        this.analyze();

        if (Project.currentFile) {
            Editor.openFile(Project.currentFile);
        }

        alert(`${fixed}개의 안전한 수정이 적용되었습니다.`);
    },

    newProject() {
        if (!confirm("현재 프로젝트를 닫을까요?")) return;

        Project.clear();

        document.getElementById("workspace").classList.add("hidden");
        document.getElementById("uploadView").classList.remove("hidden");

        document.getElementById("codeEditor").value = "";
        document.getElementById("issueList").innerHTML = "";
    }
};

document.addEventListener("DOMContentLoaded", () => {
    App.init();
});
