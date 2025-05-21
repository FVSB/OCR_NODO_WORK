from extract_info import ExtractInfo
from pypdf import PdfReader
from pathlib import Path
from dotenv import load_dotenv
from utils import find_words_starting_with, get_text_from_pdf
import os
import requests


def fetch_crossref_data(url):
    """Fetch data from CrossRef API using the provided URL.

    Args:
        url (_type_): _description_

    Returns:
        _type_: _description_
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        # Check if there are any items in the response
        if (
            "message" in data
            and "items" in data["message"]
            and len(data["message"]["items"]) > 0
        ):
            return data["message"]["items"]
        else:
            return None
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None


def files_with_extension(directory, extension):
    """Give the all files in the directory with the extension

    Args:
        directory (_type_): the relative path to the directory
        extension (_type_): the extension example pdf  without the dot (.)

    Returns:
        _type_: _description_
    """
    directory = Path(directory)
    return [str(file.resolve()) for file in directory.rglob(f"*{extension}")]


def extract_metadata(pdf_path: str) -> tuple[str, list[str], str | None]:
    """
    Extract from PDF file the metadata
    Returns: Title, Authors:list[str], DOI
    """
    reader = PdfReader(pdf_path)
    metadata = reader.metadata
    title = metadata.title
    authors = metadata.author
    doi = metadata["/doi"] if "/doi" in metadata else None
    return title, list(map(str.lstrip, authors.split(","))), doi


def get_doi_from_title(title: str) -> str | None:
    """
    Get DOI from title using CrossRef API
    """
    # Replace spaces with '+' for the query
    title = title.replace(" ", "+")
    url = f"https://api.crossref.org/works?query.title={title}&rows=1"

    data: list[dict] = fetch_crossref_data(url)

    if data:
        # Extract the DOI from the first item in the response
        doi = data[0].get("DOI", None)
        return doi
    else:
        return None


def _make_table_from_doi(doi: str):
    print(f"Doi: {doi}")
    if not doi:
        return False
    obj = ExtractInfo(
        "Publicaciones",
        "https://minube.uh.cu",
        os.environ.get("UH_CLOUD_ID"),
        os.environ.get("UH_CLOUD_PASSWORD"),
    )
    return obj.upload_data(doi)


def extract_doi_from_text(document_path: str) -> list[str]:
    dc_str = get_text_from_pdf(document_path)
    return find_words_starting_with(dc_str, "https://doi.org")


def extract_data():
    files_path: list[str] = files_with_extension("shared", "pdf")

    print(files_path)
    for file_path in files_path:
        title, authors, doi = extract_metadata(file_path)

        # If doi it,s not ( None or "")  extract metadata from this
        if doi and _make_table_from_doi(doi):
            print("Process_from doi")
            return
        elif _make_table_from_doi(get_doi_from_title(title)):  # If not doi
            # Extract from the real title the doi.
            print("Process_from title")
            return
        # elif any(map(_make_table_from_doi,extract_doi_from_text(file_path))):
        #    print("Extract from doi text extract ")
        #    return

        else:
            print("Hace falta OCR")


def main():
    # Load env vars
    load_dotenv()

    extract_data()


if __name__ == "__main__":
    main()
