from setuptools import setup, find_packages

setup(
    name="sap_autocode",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "anthropic==0.72.1",
        "openai==2.7.1",
        "pdfplumber==0.11.8",
        "PyPDF2==3.0.1",
        "python-docx==1.2.0",
        "python-dotenv==1.2.1",
        "docxtpl==0.20.1",
        "pydantic==2.12.4",
        "rich==13.7.1",
    ],
)
