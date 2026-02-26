import requests
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate

import requests
import re
from typing import Dict, Any
from loguru import logger
from dotenv import load_dotenv

from pydantic import create_model, Field
from langchain_core.tools import StructuredTool


load_dotenv(verbose=True)

BASE_URL = "http://localhost:8000"
OPENAI_URL = f"{BASE_URL}/swagger.json"

openapi_spec = requests.get(OPENAI_URL).json()
logger.info(f"OpenAI spec: {openapi_spec}")



def generate_tools(spec: Dict[str, Any]):
    tools = []

    # get("paths", {}) previne erros caso o swagger venha vazio
    for path, methods in spec.get("paths", {}).items():
        for method, details in methods.items():
            logger.info(f"Path: {path}, Method: {method}")

            # Só vamos tratar GET que tenha um dicionário de detalhes
            if method.lower() != "get" or not isinstance(details, dict):
                continue

            summary = details.get("summary", f"{method.upper()} {path}")
            logger.info(f"Summary: {summary}")

            # 🔹 Passamos o path, method e summary para a função criadora
            def make_tool(p, m, desc):
                # 1. Encontra todos os parâmetros na URL. Ex: "/problems/{id}" -> ["id"]
                param_names = re.findall(r"\{(.*?)\}", p)

                # 2. Cria dinamicamente os campos esperados para a IA preencher
                fields = {}
                for name in param_names:
                    # Definimos que a IA deve enviar uma string para cada parâmetro encontrado
                    fields[name] = (str, Field(..., description=f"Valor para o parâmetro {name} na URL"))

                # 3. Cria o Schema Pydantic dinâmico com base nos campos
                schema_name = f"{m}_{p}_Schema".replace("/", "_").replace("{", "").replace("}", "")
                DynamicSchema = create_model(schema_name, **fields)

                # 4. Nossa função agora aceita argumentos flexíveis (**kwargs)
                def call_endpoint(**kwargs):
                    # O .format() injeta os kwargs direto na string.
                    # Ex: p="/problems/{id}", kwargs={"id": "5"} -> "/problems/5"
                    endpoint = p.format(**kwargs)
                    url = f"{BASE_URL}{endpoint}"

                    logger.info(f"Invocando URL gerada: {url}")
                    response = requests.request(m.upper(), url)

                    try:
                        return response.json()
                    except Exception:
                        return response.text

                # 5. Retorna a ferramenta passando o Schema dinâmico (args_schema)
                tool_name = f"{m}_{p}".replace("/", "_").replace("{", "").replace("}", "")

                return StructuredTool.from_function(
                    func=call_endpoint,
                    name=tool_name,
                    description=desc,
                    args_schema=DynamicSchema  # A mágica acontece aqui!
                )

            tools.append(make_tool(path, method, summary))

    return tools


tools = generate_tools(openapi_spec)
logger.info(f"Tools: {tools}")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.95
)

logger.info(f"LLM: {llm}")

system_prompt = "Você é um assistente que usa ferramentas para consultar uma API."

agent_executor = create_agent(
    model=llm,
    tools=tools
)

if __name__ == "__main__":
    inputs = {
        "messages": [("human", "Retorne as estatisticas dos problemas e depois quero que retorne as informações dos problemas que estão fechados, seja criativa na resposta e responda como um pirata")]
    }

    logger.info(f"Process...\n")
    response = agent_executor.invoke(inputs)

    logger.info(f"Response: {response}")
    logger.info(f"Output: {response["messages"][-1].content}")