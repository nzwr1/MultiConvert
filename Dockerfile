# Usa una imagen base con Python
FROM python:3.10

# Instala LibreOffice y dependencias del sistema
RUN apt-get update && \
    apt-get install -y libreoffice && \
    apt-get clean

# Crea carpeta y copia archivos del proyecto
WORKDIR /app
COPY . .

# Instala dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto de Flask
EXPOSE 8000

# Comando para correr tu app
CMD ["python", "main.py"]