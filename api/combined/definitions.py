from unittest.mock import Base
from pydantic import BaseModel,Field



class ISBNResponse(BaseModel):
    isbn_print:str
    isbn_electronic:str
    

class ISSNResponse(BaseModel):
    issn_print:str
    issn_electronic:str    
