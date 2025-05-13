from markitdown import MarkItDown
import openai
import instructor
from pydantic import BaseModel
from typing import Type, TypeVar, List


class BasicResult(BaseModel):
    result: str

class BooleanResult(BaseModel):
    result:bool

def file_to_markdown_str(
    file_path: str, openai_client: openai.OpenAI = None, llm_model: str = None
) -> str:
    if openai_client is None or llm_model is None:
        md = MarkItDown(enable_plugins=False)  # Set to True to enable plugins
    else:
        md = MarkItDown(llm_client=openai_client, llm_model=llm_model)

    result = md.convert(file_path)
    return str(result)


T = TypeVar("T", bound=BaseModel)


class DocumentChat:
    def _ask_document(self,query:str,response_format:dict):
        chat_completion = self.api_client.chat.completions.create(
            model=self.llm_model,
            response_format=response_format,
            messages=[
                {"role": "system", "content": f"{self.system_prompt}"},
                {"role": "system", "content": self.file_context},
                {"role": "user", "content": query},
            ],
            temperature=self.temperature
            
        )
        return  chat_completion.choices[0].message.content
    def ask_with_gbnf_grammar(self,query:str, grammar:str):
        
        #TODO: Comprobar que la gramatica es gbnf
        
        response_format={"type": "grammar", "grammar": grammar}
        
        return self._ask_document(query,response_format)
    
    def ask_with_json_format(self, query: str, jsonSchema: Type[T]) -> T:
        """
        Given a query and a pydantic schema return the response in a pydantic object with this schema

        Args:
            query (str): _description_
            jsonSchema (BaseModel): _description_

        Raises:
            Exception: _description_

        Returns:
            BaseModel: _description_
        """
        if not issubclass(jsonSchema, BaseModel):
            raise Exception(
                f"jsonSchema must be subclass of BaseModel pydantic object not {type(jsonSchema)}"
            )
        response=self._ask_document(query,{
                "type": "json_object",
                "schema": jsonSchema.model_json_schema(),
            })
        return jsonSchema.model_validate_json(
           response
        )

    def ask_document(self, query: str)->str:
        temp = self.ask_with_json_format(query, self.default_json_schema)
        return temp.result

    def boolean_ask_document(self,query:str)->bool:
        temp = self.ask_with_json_format(query, BooleanResult)
        return temp.result
    
    def __init__(
        self,
        document_path: str,
        openai_base_url: str,
        openai_api_key: str,
        llm_model: str,
        system_prompt: str,
        default_json_schema: BaseModel = BasicResult,
        temperature:float=0
    ):
        self.original_path: str = document_path
        self.file_context: str = file_to_markdown_str(document_path)
        self.api_client: openai.OpenAI = openai.OpenAI(
            base_url=openai_base_url, api_key=openai_api_key
        )
        self.system_prompt: str = system_prompt
        self.llm_model: str = llm_model
        self.default_json_schema: BaseModel = default_json_schema
        self.temperature:float=temperature
        
        
        
class DocumentChatOllama(DocumentChat):
    def __init__(
        self,
        document_path: str,
        openai_base_url: str,
        openai_api_key: str,
        llm_model: str,
        system_prompt: str,
        default_json_schema: BaseModel = BasicResult,
        temperature:float=0
    ):
        
        
        super().__init__(document_path, openai_base_url, openai_api_key, llm_model, system_prompt, default_json_schema,temperature)
        self.api_client=instructor.from_openai(
        super().api_client,
    mode=instructor.Mode.JSON,
)
        