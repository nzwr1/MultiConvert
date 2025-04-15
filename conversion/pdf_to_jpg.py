from pdf2image import convert_from_bytes
import uuid
import os

def convert_pdf_to_jpg(pdf_file, output_folder):
    images = convert_from_bytes(pdf_file.read(), fmt='jpeg', dpi=200)
    image_paths = []

    for i, image in enumerate(images):
        filename = f"{uuid.uuid4().hex}_page_{i + 1}.jpg"
        path = os.path.join(output_folder, filename)
        image.save(path, 'JPEG')
        image_paths.append(path)

    return image_paths