window.pdf_to_jpg = async () => {
    const fileInput = document.getElementById('pdf-file');
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
  
    const response = await fetch('/convert_pdf_to_jpg', {
      method: 'POST',
      body: formData
    });
  
    const result = await response.json();
  
    const gallery = document.getElementById('gallery');
    gallery.innerHTML = '';
  
    if (result.images) {
      result.images.forEach(url => {
        const img = document.createElement('img');
        img.src = url;
        img.style.maxWidth = '200px';
        img.style.margin = '10px';
        gallery.appendChild(img);
      });
    } else {
      gallery.innerHTML = '<p>Error al convertir el archivo.</p>';
    }
  };
  