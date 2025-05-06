import subprocess
import os

def convert_word_to_pdf(input_path, output_path):
    try:
        subprocess.run([
            "libreoffice", "--headless", "--convert-to", "pdf", "--outdir",
            os.path.dirname(output_path), input_path
        ], check=True)
        return output_path
    except subprocess.CalledProcessError as e:
        raise Exception(f"Error converting Word to PDF: {str(e)}")
