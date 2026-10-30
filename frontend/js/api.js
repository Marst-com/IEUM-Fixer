const API = {
    baseURL: "http://127.0.0.1:8000/api",

    projectId: null,

    async request(endpoint, options = {}) {
        const response = await fetch(
            this.baseURL + endpoint,
            options
        );

        if (!response.ok) {
            const message = await response.text();
            throw new Error(message || `HTTP ${response.status}`);
        }

        return response;
    },

    async health() {
        const response = await this.request("/health");
        return response.json();
    },

    async upload(file) {
        const form = new FormData();
        form.append("file", file);

        const response = await this.request(
            "/projects/upload",
            {
                method: "POST",
                body: form
            }
        );

        const result = await response.json();

        this.projectId = result.project_id;

        return result;
    },

    async getProject() {
        const response = await this.request(
            `/projects/${this.projectId}`
        );

        return response.json();
    },

    async getFile(path) {
        const response = await this.request(
            `/projects/${this.projectId}/file?path=${encodeURIComponent(path)}`
        );

        return response.json();
    },

    async saveFile(path, content) {
        const response = await this.request(
            `/projects/${this.projectId}/file`,
            {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ path, content })
            }
        );

        return response.json();
    },

    async analyze() {
        const response = await this.request(
            `/projects/${this.projectId}/analyze`,
            { method: "POST" }
        );

        return response.json();
    },

    async repair(issueId) {
        const response = await this.request(
            `/projects/${this.projectId}/repair`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    issue_id: issueId
                })
            }
        );

        return response.json();
    },

    async repairAll() {
        const response = await this.request(
            `/projects/${this.projectId}/repair/safe-all`,
            { method: "POST" }
        );

        return response.json();
    },

    async validate() {
        const response = await this.request(
            `/projects/${this.projectId}/validate`,
            { method: "POST" }
        );

        return response.json();
    },

    async download() {
        const response = await this.request(
            `/projects/${this.projectId}/download`
        );

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);

        const link = document.createElement("a");
        link.href = url;
        link.download = "IEUM-Fixer-Recovered.zip";
        link.click();

        setTimeout(() => URL.revokeObjectURL(url), 2000);
    }
};
