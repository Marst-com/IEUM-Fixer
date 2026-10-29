
const ZipManager = {
    async extract(file) {
        if (typeof JSZip === "undefined") {
            throw new Error("JSZip 라이브러리를 불러오지 못했습니다.");
        }

        const zip = await JSZip.loadAsync(file);
        const entries = Object.values(zip.files);

        for (const entry of entries) {
            if (entry.dir) continue;

            const path = entry.name.replace(/\\/g, "/");

            if (
                path.startsWith("/") ||
                path.split("/").some(part => part === "..")
            ) {
                continue;
            }

            if (entry._data?.uncompressedSize > 10 * 1024 * 1024) {
                continue;
            }

            if (entry.name.includes("/node_modules/") ||
                entry.name.startsWith("node_modules/") ||
                entry.name.includes("/.git/") ||
                entry.name.startsWith(".git/")) {
                continue;
            }

            const content = await entry.async("string");
            Project.addFile(path, content);
        }
    },

    async download() {
        const zip = new JSZip();

        for (const [path, file] of Project.files) {
            zip.file(path, file.content);
        }

        const blob = await zip.generateAsync({
            type: "blob",
            compression: "DEFLATE",
            compressionOptions: { level: 6 }
        });

        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");

        link.href = url;
        link.download = `${Project.name}-fixed.zip`;
        link.click();

        setTimeout(() => URL.revokeObjectURL(url), 1000);
    }
};
