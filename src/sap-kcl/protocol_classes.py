import PyPDF2
import os

class Protocol:
    def __init__(self, file_path):
        self.file_path = file_path
        ext = self.check_file_extension(file_path)
        if ext == '.pdf':
            self.load_pdf()
        if ext == '.txt':
            self.load_txt()

    def load_pdf(self):
        protocol = ""
        with open(self.file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            num_pages = len(reader.pages)
            for i in range(num_pages):
                page = reader.pages[i]
                protocol += page.extract_text()
        self.protocol_txt = protocol

    def load_txt(self):
        with open(self.file_path, "r") as file:
            protocol = file.read()
        self.protocol_txt = protocol

    def save_protocol_txt(self, protocol_txt_path):
            with open(protocol_txt_path, "w", encoding="utf-8") as txt_file:
                txt_file.write(self.protocol_txt)

    def check_file_extension(self, filename):
        _, ext = os.path.splitext(filename)

        if ext.lower() not in ['.txt', '.pdf']:
            raise ValueError(f"Unsupported file extension: {ext}. Must be .txt or .pdf")

        return ext
