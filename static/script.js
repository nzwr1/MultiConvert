document.addEventListener("DOMContentLoaded", () => {
  const fileInput = document.getElementById("pdfFile");
  const status = document.getElementById("estado");
  const fileNameElement = document.getElementById("fileName");
  
  // Esta función se ejecuta cuando se selecciona un archivo
  fileInput.addEventListener("change", handleFileSelected);

  // Maneja la selección de archivo
  function handleFileSelected() {
    const archivo = fileInput.files[0];
    if (archivo) {
      fileNameElement.textContent = "Archivo seleccionado: " + archivo.name;
    }
  }

  // Esta función se ejecuta cuando se hace clic en el botón de convertir
  window.convertPDF = async () => {
    const archivo = fileInput.files[0];
    if (!archivo || !archivo.name.endsWith(".pdf")) {
      alert("Por favor, selecciona un archivo .pdf");
      return;
    }

    // Mostrar mensaje de "Convirtiendo"
    status.textContent = "Convirtiendo, espera un momento...";

    const formData = new FormData();
    formData.append("file", archivo);

    try {
      const response = await fetch("/pdf-to-word", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        status.textContent = "Ocurrió un error en la conversión.";
        return;
      }

      const disposition = response.headers.get("Content-Disposition");
      let filename = "documento.docx";
      if (disposition && disposition.includes("filename=")) {
        filename = disposition.split("filename=")[1].replace(/"/g, "");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      a.click();
      window.URL.revokeObjectURL(url);

      status.textContent = "¡Conversión completa!";  // Mensaje de éxito
    } catch (error) {
      console.error("Error:", error);
      status.textContent = "Error al subir el archivo.";
    }
  };
});

document.addEventListener("DOMContentLoaded", () => {
  const fileInput = document.getElementById("mp4File");
  const status = document.getElementById("estado");
  const fileNameElement = document.getElementById("fileName");
  
  // Esta función se ejecuta cuando se selecciona un archivo
  fileInput.addEventListener("change", handleFileSelected);

  // Maneja la selección de archivo
  function handleFileSelected() {
    const archivo = fileInput.files[0];
    if (archivo) {
      fileNameElement.textContent = "Archivo seleccionado: " + archivo.name;
    }
  }

  // Esta función se ejecuta cuando se hace clic en el botón de convertir
  window.convert_mp3 = async () => {
    const archivo = fileInput.files[0];
    if (!archivo || !archivo.name.endsWith(".mp4")) {
      alert("Por favor, selecciona un archivo .mp4");
      return;
    }

    // Mostrar mensaje de "Convirtiendo"
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

      const disposition = response.headers.get("Content-Disposition");
      let filename = "audio.mp3";
      if (disposition && disposition.includes("filename=")) {
        filename = disposition.split("filename=")[1].replace(/"/g, "");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      a.click();
      window.URL.revokeObjectURL(url);

      status.textContent = "¡Conversión completa!";  // Mensaje de éxito
    } catch (error) {
      console.error("Error:", error);
      status.textContent = "Error al subir el archivo.";
    }
  };
});

// Mostrar nombre de archivo seleccionado
function handleFileSelected() {
  const input = document.getElementById('mp4File');
  const fileNameElement = document.getElementById('fileName');
  
  const selectedFile = input.files[0];
  if (selectedFile) {
    fileNameElement.textContent = "Archivo seleccionado: " + selectedFile.name;
  }
}

// ** Actualizar la lógica de conversión al PDF a Word **
let selectedFile = null;
function handlePDFFileSelected() {
  const input = document.getElementById('pdfFile');
  selectedFile = input.files[0];

  if (selectedFile) {
    document.getElementById('fileName').textContent = "Archivo seleccionado: " + selectedFile.name;
  }
}

function convertPDF() {
  if (!selectedFile) {
    alert("Por favor, seleccioná un archivo PDF.");
    return;
  }

  const formData = new FormData();
  formData.append('file', selectedFile);

  fetch('/pdf-to-word', {
    method: 'POST',
    body: formData
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('La conversión falló.');
    }
    return response.blob();
  })
  .then(blob => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = selectedFile.name.replace('.pdf', '.docx');
    a.click();
    window.URL.revokeObjectURL(url);
  })
  .catch(error => {
    console.error(error);
    alert('Hubo un problema al convertir el archivo.');
  });
}

  
  