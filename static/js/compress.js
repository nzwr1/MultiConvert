let archivoSeleccionado = null;

function handleFileSelected() {
  const input = document.getElementById("archivo");
  archivoSeleccionado = input.files[0];
  document.getElementById("fileName").textContent = archivoSeleccionado.name;
}

async function comprimirArchivo() {
  if (!archivoSeleccionado) {
    document.getElementById("estado").textContent = "Primero seleccioná un archivo.";
    return;
  }

  document.getElementById("estado").textContent = "Procesando...";

  const formData = new FormData();
  formData.append("file", archivoSeleccionado);

  try {
    const response = await fetch("/compress", {
      method: "POST",
      body: formData
    });

    if (!response.ok) {
      const errorText = await response.text();
      document.getElementById("estado").textContent = "Error: " + errorText;
      return;
    }

    const blob = await response.blob();
    const filename = response.headers.get("Content-Disposition").split("filename=")[1];

    const link = document.createElement("a");
    link.href = window.URL.createObjectURL(blob);
    link.download = filename;
    link.click();

    document.getElementById("estado").textContent = "Archivo comprimido exitosamente.";
  } catch (error) {
    document.getElementById("estado").textContent = "Error al procesar el archivo.";
    console.error(error);
  }
}
