
const Project = {
    files: new Map(),
    currentFile: null,
    issues: [],
    name: "Untitled Project",

    addFile(path, content) {
        this.files.set(path, {
            path,
            content,
            original: content,
            modified: false
        });
    },

    getFile(path) {
        return this.files.get(path);
    },

    updateFile(path, content) {
        const file = this.files.get(path);
        if (!file) return;

        file.content = content;
        file.modified = file.content !== file.original;
    },

    clear() {
        this.files.clear();
        this.issues = [];
        this.currentFile = null;
        this.name = "Untitled Project";
    },

    getFileCount() {
        return this.files.size;
    }
};
