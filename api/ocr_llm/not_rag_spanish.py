import os
from dotenv import load_dotenv

# 1. Carga las variables de entorno desde .env
load_dotenv()


from llm_structure import DocumentChat


system_prompt = "Hello, your mission will be to help me extract information from the following documents your context is only this document, you never say nothing is not in the context. You will respond briefly and always in JSON {} format. Siempre responde en idioma Español."


chat = DocumentChat(
    "document.pdf",
    "https://api.fireworks.ai/inference/v1",
    os.environ.get("FIREWORKS_API"),
    "accounts/fireworks/models/llama-v3p1-8b-instruct",
    system_prompt,
)


# chat=DocumentChat("document.pdf","http://localhost:11434/v1","ollama","llama3.2:latest",system_prompt)


query = chat.ask_document

query_boolean = chat.boolean_ask_document

is_in_english=query_boolean("The document is in English?")

# ## Titulo del documento


title = query("Give me the title of the document")


# ## Autores


authors = query("Dime los nombres de los autores?")


# ## Decir si es un articulo o una publicacion


def query_grammar(query, prepositions: list[str]):
    root_grammar = f"""
    root ::= response
    response ::= {' | '.join(f'"{item}"' for item in prepositions)}
    """
    return chat.ask_with_gbnf_grammar(query, root_grammar)


query_grammar(
    "Es documento es un articulo cientifico o es un libro?", ["Libro", "Articulo"]
)


year = query("En que año se publico el articulo?")


editor = query("Cual es el nombre de la editorial?")


country = query("Cual es el pais de publicacion?")


publish_url = query("Cual es la url de publicación?")


author_ocid = query("Cual es el orcid de cada autor?")


document_doi = query("Cual es el doi del documento?")


is_paper = query("Cual es el tipo de medio de divulgación?")


location_in_uh = query("Desde que area se reporta?")


is_from_a_proyect = query_boolean(
    "El documento tributa a algun proyecto de ciencia o investigación? no vale la revista tipo"
)

if is_from_a_proyect:
    proyects_name = query(
        "Cual es el proyecto de ciencia e investigacion al que tributa? No vale la revista tipo "
    )



