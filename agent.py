import requests
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import StructuredTool
from loguru import logger
from dotenv import load_dotenv

from apagar import system_prompt, agent_executor

load_dotenv(verbose=True)

BASE_URL = "http://localhost:8000"
OPENAI_URL = f"{BASE_URL}/swagger.json"

openapi_spec = requests.get(OPENAI_URL).json()
logger.info(f"OpenAI spec: {openapi_spec}")

def generate_tools(spec: Dict[str, Any]):
    tools = []

    for path, methods in spec["paths"].items():
        for method, details in methods.items():
            logger.info(f"Path: {path}, Method: {method}, Details: {details}")
            if method.lower() != "get" or not isinstance(details, dict):
                continue
            summary = details.get("summary", f"{method.upper()} {path}")
            logger.info(f"Summary sdrsrwe: {summary}")

            def make_tool(p, m):
                def call_endpoint(city:str):
                    endpoint = p.replace("{city}", city)
                    url = f"{BASE_URL}{endpoint}"
                    response = requests.request(m.upper(), url)
                    logger.info(f"Response: {response.text}")
                    return response.json()
                return StructuredTool.from_function(
                    func=call_endpoint,
                    name=f"{m}_{p}".replace("/", "_").replace("{", "").replace("}", ""),
                    description=summary
                )
            tools.append(make_tool(path, method))
    return tools


tools = generate_tools(openapi_spec)
logger.info(f"Tools: {tools}")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)

logger.info(f"LLM: {llm}")

system_prompt = "Você é um assistente que usa ferramentas para consultar uma API de clima."

agent_executor = create_agent(
    model=llm,
    tools=tools
)

if __name__ == "__main__":
    inputs = {
        "messages": [("human", "Como está o clima amanhã em Manaus?")]
    }

    logger.info(f"Process...\n")
    response = agent_executor.invoke(inputs)

    logger.info(f"Response: {response}")
    logger.info(f"Output: {response["messages"][-1].content}")