from docx2pdf import convert

def convert_word_to_pdf(input_path, output_path):
    try:
        convert(input_path, output_path)
        return output_path
    except Exception as e:
        raise Exception(f"Error converting Word to PDF: {str(e)}")
