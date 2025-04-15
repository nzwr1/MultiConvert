document.addEventListener("DOMContentLoaded", () => {
    const fileInput = document.getElementById("mp4File");
    const status = document.getElementById("estado");
    const fileNameElement = document.getElementById("fileName");
  
    fileInput.addEventListener("change", () => {
      const archivo = fileInput.files[0];
      if (archivo) {
        fileNameElement.textContent = "Archivo seleccionado: " + archivo.name;
      }
    });
  
    window.convert_mp3 = async () => {
      const archivo = fileInput.files[0];
      if (!archivo || !archivo.name.endsWith(".mp4")) {
        alert("Por favor, selecciona un archivo .mp4");
        return;
      }
  
      status.textContent = "Convirtiendo, espera un momento...";
  
      const formData = new FormData();
      formData.append("archivo", archivo);
  
      try {
        const response = await fetch("/convert_mp3", {
          method: "POST",
          body: formData,
        });
  
        if (!response.ok) {
          status.textContent = "Ocurrió un error en la conversión.";
          return;
        }
  
        const blob = await response.blob();
        const disposition = response.headers.get("Content-Disposition");
        const filename = disposition?.split("filename=")[1]?.replace(/"/g, "") || "audio.mp3";
  
        const a = document.createElement("a");
        a.href = window.URL.createObjectURL(blob);
        a.download = filename;
        a.click();
  
        window.URL.revokeObjectURL(a.href);
        status.textContent = "¡Conversión completa!";
      } catch (error) {
        console.error("Error:", error);
        status.textContent = "Error al subir el archivo.";
      }
    };
  });
  