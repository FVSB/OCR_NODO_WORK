
from markitdown import MarkItDown


def find_words_starting_with(text:str, substring:str):
    """
    Returns a list of all substrings in 'text' that start with 'substring' and end at the next whitespace.
    """
    words = []
    start = 0
    text_len = len(text)
    while True:
        index = text.find(substring, start)
        if index == -1:
            break

        # Find end of the word (next space/newline/tab or end of text)
        end = index
        while end < text_len and not text[end].isspace():
            end += 1

        word = text[index:end]
        words.append(word)
        start = end   # Continue searching after the current word

    return words




def get_text_from_pdf(pdf_path:str)->str:


    md = MarkItDown(enable_plugins=True) # Set to True to enable plugins
    result = md.convert("document.pdf")
    return result.text_content
    