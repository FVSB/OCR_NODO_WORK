from abc import ABC, abstractmethod
from pydoc import doc
from xml.dom.minidom import DocumentType

from pydantic import BaseModel
from typing import Type, TypeVar, List

from ..ocr_llm.llm_structure import DocumentChat
from datetime import datetime
from enum import Enum
import requests
import traceback


T = TypeVar("T", bound=BaseModel)


class TypeDocument(Enum):
    science_articule = "science_articule"
    book = "book"
    book_chapter="book_chapter"
    monograph="monograph"
    conference_paper="conference_paper"
    no_match="no_match"

class TypeDocumentWithOther(TypeDocument):
    other = "other"

class Means_Of_Dissemination(Enum):
    press_media="press_media"
    science_magazine="science_magazine"
    blog="blog"
    not_articule="not_articule"
    other="other"
    
class DocumentExtractor(ABC):
    """
    Abstract base class for document extractors.
    """
    @abstractmethod
    def get_doi(self)->str|None:
        
        pass
    
    @abstractmethod
    def get_title(self) -> str | None:
        """
        Gets the title of the document.

        Returns:
            str: The title of the document.
        """
        pass

    @abstractmethod
    def get_external_authors(self) -> list[str] | None:
        """
        Gets the external authors of the document.

        Returns:
            list[str]: A list of external authors.
        """
        pass

    @abstractmethod
    def get_editorial(self) -> str | None:
        """
        Gets the editorial of the document.

        Returns:
            str: The editorial of the document.
        """
        pass

    @abstractmethod
    def get_issns_or_isbn(self) -> tuple[str] | None:
        """
        Gets the ISSNs of the document.
        The electronic ISSN is the first one in the tuple.


        Returns:
            tuple[str]: A tuple containing the ISSNs. The electronic ISSN is the first one in the tuple.
        """
        pass

    @abstractmethod
    def get_country_published(self) -> str | None:
        """
        Gets the country of publication of the document.

        Returns:
            str: The country of publication of the document.
        """
        pass

    @abstractmethod
    def get_country_published(self) -> str | None:
        """
        Gets the country of publication of the document.

        Returns:
            str: The country of publication of the document.
        """
        pass

    @abstractmethod
    def get_url(self) -> str | None:
        """
        Gets the URL of the document.

        Returns:
            str: The URL of the document.
        """
        pass

    @abstractmethod
    def get_internal_authors(self) -> list[str] | None:
        """
        Gets the internal authors of the document.

        Returns:
            list[str]: A list of internal authors.
        """
        pass

    @abstractmethod
    def get_science_network(self) -> str | None:
        """
        Gets the science network of the document.

        Returns:
            str: The science network of the document.
        """
        pass

    @abstractmethod
    def get_founders(self) -> list[tuple[str]] | None:
        """AI is creating summary for get_founders

        Returns:
            str: [description]
        """
        pass

    @abstractmethod
    def get_year(self) -> int | None:
        """
        Gets the year of publication of the document.

        Returns:
            str: The year of publication of the document.
        """
        pass

    @abstractmethod
    def get_publish_type(self) -> int | None:
        """
        Gets the type of publication of the document.

        Returns:
            str: The type of publication of the document.
        """
        pass

    @abstractmethod
    def get_publish_group(self) -> int | None:
        """
        Gets the publishing group of the document.

        Returns:
            str: The publishing group of the document.
        """
        pass

    @abstractmethod
    def get_serial_type(self) -> list[int] | None:
        """
        Gets the serial type of the document.

        Returns:
            str: The serial type of the document.
        """
        pass

    @abstractmethod
    def get_is_international(self) -> bool | None:
        """
        Checks if the document is international.

        Returns:
            bool: True if the document is international, False otherwise.
        """
        pass

    @abstractmethod
    def get_origin_external_authors(self) -> int | None:
        """
        Gets the origin of the external authors of the document.

        Returns:
            int: The origin of the external authors of the document.
        """
        pass

    @abstractmethod
    def get_is_external_principal_author(self) -> bool | None:
        """
        Checks if the principal author is external.

        Returns:
            bool: True if the principal author is external, False otherwise.
        """
        pass

    @abstractmethod
    def get_means_of_dissemination(self) -> Means_Of_Dissemination | None:
        """
        Gets the means of dissemination of the document.

        Returns:
            int: The means of dissemination of the document.
        """
        pass

    @abstractmethod
    def get_quartile(self) -> int:
        """
        Gets the quartile of the document.

        Returns:
            int: The quartile of the document.
        """
        pass

    @abstractmethod
    def get_report_area(self) -> tuple[str, str] | None:
        """
        Gets the report area of the document.

        Returns:
            tuple[str,str]: A tuple containing the report area and subarea of the document.
        """
        pass

    @abstractmethod
    def extract(self, file_path: str) -> dict | None:
        """
        Extracts data from a document.

        Args:
            file_path (str): The path to the document file.

        Returns:
            dict: A dictionary containing the extracted data.
        """
        pass

    ###


############
#
# CrossRefExtractor
#
#############


def get_country_editorial_by_doi(doi) -> str:
    # Paso 1: Obtener metadata del artículo
    url_work = f"https://api.crossref.org/works/{doi}"
    resp = requests.get(url_work)
    if resp.status_code != 200:
        return "DOI no encontrado"
    data = resp.json()

    # Paso 2: Extraer member_id
    member_url = data["message"].get("member")
    if not member_url:
        return "No se encontró el member_id"
    member_id = member_url.split("/")[-1]

    # Paso 3: Consultar la API de miembros
    url_member = f"https://api.crossref.org/members/{member_id}"
    resp_member = requests.get(url_member)
    if resp_member.status_code != 200:
        return "No se encontró información del miembro"
    data_member = resp_member.json()

    # Paso 4: Extraer país
    country_code = data_member["message"].get("location", "País no disponible")
    publisher = data_member["message"].get("primary-name", "Editorial desconocida")

    # return f"Editorial: {publisher}, País (código ISO): {country_code}"
    return country_code


def get_from_crossref(doi: str) -> dict:
    """
    Get Data from crossref

    Args:
        doi (str): _description_

    Returns:
        dict: _description_
    """
    url = f"https://api.crossref.org/works/{doi}"
    response = requests.get(url)
    data = response.json()
    return data["message"]


def get_editorial_name_by_issn(issn: str):
    url = f"https://api.crossref.org/journals/{issn}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data["message"].get("publisher", "Editorial no encontrada")
    else:
        return f"Error en la consulta: {response.status_code}"




class CrossRefExtractor(DocumentExtractor):
    """
    Class for extracting data from CrossRef documents.
    """

    def define_type_document(self) -> TypeDocumentWithOther:
        match self.data["type"]:
            case "journal-articule":
                return TypeDocumentWithOther.articule
            case "book":
                return TypeDocumentWithOther.book
            case _:
                return TypeDocumentWithOther.other
        return TypeDocumentWithOther.other

    def __init__(self, doi: str):
        self.doi: str = doi
        self.data: dict = get_from_crossref(doi)
        self.type_document: TypeDocumentWithOther = self.define_type_document()

    def _get_authors_obj(self) -> dict:
        """
        Returns the authors obj
        """
        return self.data["author"]

    def _get_authors(self, is_internal: bool):
        """
        Get authors from the data.
        """
        authors = self._get_authors_obj()
        lis = []
        if is_internal:
            lis = [
                author
                for author in authors
                if any(
                    aff["name"] == "Universidad de La Habana"
                    for aff in author["affiliation"]
                )
            ]
        else:
            lis = [
                author
                for author in authors
                if not any(
                    aff["name"] == "Universidad de La Habana"
                    for aff in author["affiliation"]
                )
            ]

        temp: str = ""
        for external in lis:
            temp += f"{external["family"] } {external["given"][0]}, "
        return temp

    def get_title(self) -> str | None:
        try:
            return self.data["title"][0]
        except Exception as e:
            print(f"Error in get_title: {e}")
            return None

    def get_external_authors(self) -> list[str] | None:
        try:
            return self._get_authors(is_internal=False)
        except Exception as e:
            return None

    def get_internal_authors(self) -> list[str] | None:
        try:
            return self._get_authors(is_internal=True)
        except Exception as e:
            return None

    def get_is_external_principal_author(self) -> bool | None:
        try:

            authors = self._get_authors_obj()
            principal_authors = [
                author for author in authors if author["sequence"] == "first"
            ]
            external_authors = [
                author
                for author in authors
                if not any(
                    aff["name"] == "Universidad de La Habana"
                    for aff in author["affiliation"]
                )
            ]

            if not principal_authors[0] in external_authors:
                return True
            return False

        except Exception as e:
            return None

    def get_editorial(self) -> str | None:
        try:
            issn = self.data["ISSN"][0]
            return get_editorial_name_by_issn(issn)
        except Exception as e:
            print(f"Error in get_editorial: {e}")
            return None

    def get_issns_or_isbn(self) -> tuple[str] | None:
        try:
            issns_type = (
                self.data["issn-type"]
                if self.type_document == TypeDocumentWithOther.science_articule
                else self.data["isbn-type"]
            )
            issns_print = None
            issns_electronic = None
            for item in issns_type:
                value = item["value"]
                item_type = item["type"]
                if item_type == "electronic":
                    issns_electronic = value
                elif item_type == "print":
                    issns_print = value
            return issns_electronic, issns_print
        except Exception as e:
            return None

    def get_country_published(self) -> str | None:
        try:
            return get_country_editorial_by_doi(self.doi)
        except Exception as e:
            return None

    def get_url(self) -> str | None:
        try:
            return f'{"{"}{"\""}title{"\""}:{"\""}{self.doi}{"\""},{"\""}subline{"\""}:{"\""}URL{"\""},{"\""}providerId{"\""}:url,{"\""}value{"\""}:{"\""}{self.doi}{"\""}'
        except Exception as e:
            return None

    def get_science_network(self) -> str | None:
        return None

    def get_founders(self) -> list[tuple[str]] | None:
        """
        Returns the founder name , founder award if exists the info
        """
        try:
            founders = self.data["funder"]
            temp = ""
            lis: list[tuple[str]] = []
            for founder in founders:
                # temp += f"{founder["name"]}, {founder["award"] if "award" in founder else "" }, \n"
                lis.append(
                    (founder["award"], founder["award"] if "award" in founder else "")
                )
            return lis
        except Exception as e:
            return None

    def get_year(self) -> int | None:
        try:
            return self.data["indexed"]["date-parts"][0][0]
        except Exception as e:
            return None

    def get_publish_type(self) -> int | None:
        # Retorna el numero sobre el tipo de publicacion
        # Mandar al llm
        # Solo decantar si es un articulo cientifico
        # Libro, o capitulo de libro
        try:
            match self.data["type"]:
                case "journal-articule":
                    return None
                case "book":
                    return 1
                case _:
                    return None
        except Exception as e:

            return None

    def get_publish_group(self):
        # Seleccionar los grupos por tanto que lo hagan con atributos
        return None

    def get_serial_type(self) -> list[int] | None:

        try:
            lis: list[int] = []
            issns = self.get_issns_or_isbn()
            if issns[1]:
                if self.type_document == TypeDocumentWithOther.science_articule:
                    lis.append(0)
                elif self.type_document == TypeDocumentWithOther.book:
                    list.append(2)
            if issns[0]:
                if self.type_document == TypeDocumentWithOther.science_articule:
                    list.append(1)
                elif self.type_document == TypeDocumentWithOther.book:
                    list.append(3)
            return None if len(lis) == 0 else lis

        except Exception as e:
            return None

    def _exist_international_author(self) -> bool:
        authors = self._get_authors_obj()
        return any(
            "cuba" not in place.lower()
            for author in authors
            for affiliation in author.get("affiliation", [])
            for place in affiliation.get("place", [])
        )

    def get_is_international(self) -> bool | None:
        try:
            return self._exist_international_author()
        except Exception as e:
            return None

    def get_origin_external_authors(self) -> list[tuple[str]] | None:
        """
        Devolver una lista con los lugares donde
        """
        try:
            authors = self._get_authors_obj()
            reutrn = list(
                {
                    (affiliation.get("name"), place)
                    for author in authors
                    for affiliation in author.get("affiliation", [])
                    for place in affiliation.get("place", [])
                }
            )
        except Exception as e:
            return None

    def get_means_of_dissemination(self)->Means_Of_Dissemination|None:
        """
        
        """
        try:
            if self.type_document!=TypeDocumentWithOther.science_articule:
                return Means_Of_Dissemination.not_articule
            else:
                issns=self.get_issns_or_isbn()
                if  issns and (issns[0] or issns[1]):
                    return Means_Of_Dissemination.science_magazine
            
            return Means_Of_Dissemination.other
            
        except Exception as e:
            raise e
        
        
    def get_quartile(self)->int|None:
        return None
    
    def get_report_area(self):
        return None
    


    
class ClassDocumentExtractorOCR(DocumentExtractor):
    

        
    def __init__(self,llm:DocumentChat):
        self.llm:DocumentChat=llm
        
        

    def _query(self,query:str,chunk=None):
        return self.ask_document(query)  
    
    def _query_boolean(self,query:str,chunk=None)->bool:
        return self.llm.boolean_ask_document(query)
    
    def _query_with_pydantic_schema(self,query:str,schema:Type[T],chunk=None)->T:
        return self.llm.ask_with_json_format(query,schema)
        
    
    def get_doi(self):
        query="""
        Please extract the DOI (Digital Object Identifier) 
        from the following document text. A DOI is 
        a unique alphanumeric string used to 
        identify digital documents persistently. 
        It always starts with the characters '10.'
        followed by a prefix and a suffix separated 
        by a slash. The prefix identifies the 
        registrant (usually the publisher) and 
        consists of numbers after '10.', and the 
        suffix identifies the specific document. 
        For example, in the DOI '10.1000/182', 
        '10.1000' is the prefix and '182' is the 
        suffix. Look for a string matching this 
        pattern and return only the DOI.
        """
        return self._query(query)
    
    
    
    def get_title(self):
        query="""
        Tell me the title of the document.
        """   
        return self._query(query=query) 
    
    
    def get_authors(self):
        query="""
        Tell me the name of the authors.
        """    
        return self._query(query=query)
    
    def get_editorial(self):
        query="""
        Tell me the name of the editorial of this articule
        """
        return self._query(query)
    
    
    def get_type_document(self)->TypeDocument:
        query=f"""
        Given the following document text, 
        classify it as one of these categories: 
        {TypeDocument.book}, {TypeDocument.monograph}, 
        {TypeDocument.book_chapter}, {TypeDocument.science_articule}, 
        {TypeDocument.conference_paper}. If it doesn't clearly match any, 
        reply with {TypeDocument.no_match} and a brief reason. Document text:
        """
        return self._query_with_pydantic_schema(query,TypeDocument)
    
    
    
        
        
        
        