async function convertPDF() {
    const input = document.getElementById('pdfFile');
    const file = input.files[0];
    if (!file) {
        alert("Selecciona un archivo PDF primero");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);
  
        try {
            const response = await fetch("http://127.0.0.1:5000/pdf-to-word", {
            method: "POST",
            body: formData,
        });
  
        if (!response.ok) {
            throw new Error("Error al convertir el PDF");
        }
  
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
  
        const filename = file.name.replace('.pdf', '.docx');
        a.download = filename;
  
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
  
        } catch (error) {
        alert(error.message);
        }
    }
  