<input type="file" id="fileInput" @change="handleFileUpload" multiple>
<button class="select-file-btn" @click="openFileDialog">选择文件</button>

<script>
methods: {
  handleFileUpload(event) {
    const files = Array.from(event.target.files);
    this.selectedFiles = [...files];
    // 生成预览图
    files.forEach((file) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        this.previewImages.push(e.target.result);
      };
      reader.readAsDataURL(file);
    });
  },
  openFileDialog() {
    document.getElementById("fileInput").click();
  },
  confirmUpload() {
    const formData = new FormData();
    this.selectedFiles.forEach((file) => {
      formData.append("files", file);
    });
    fetch("/upload", { method: "POST", body: formData })
  }
}
</script>