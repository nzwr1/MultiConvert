document.addEventListener("DOMContentLoaded", () => {
    const fileInput = document.getElementById("wordFile");
    const status = document.getElementById("estado");
    const fileNameElement = document.getElementById("fileName");
  
    fileInput.addEventListener("change", () => {
      const archivo = fileInput.files[0];
      if (archivo) {
        fileNameElement.textContent = "Archivo seleccionado: " + archivo.name;
      }
    });
  
    window.convertWord = async () => {
      const archivo = fileInput.files[0];
      if (!archivo || !archivo.name.match(/\.docx?$/i)) {
        alert("Por favor, selecciona un archivo .docx o .doc (Word).");
        return;
      }
  
      status.textContent = "Convirtiendo, espera un momento...";
  
      const formData = new FormData();
      formData.append("file", archivo);
  
      try {
        const response = await fetch("/word-to-pdf", {
          method: "POST",
          body: formData,
        });
  
        if (!response.ok) {
          const errorText = await response.text();
          status.textContent = `Ocurrió un error: ${errorText || "No se pudo procesar el archivo."}`;
          return;
        }
  
        const blob = await response.blob();
        const disposition = response.headers.get("Content-Disposition");
        const filename = disposition?.split("filename=")[1]?.replace(/"/g, "") || "documento.pdf";
  
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
  