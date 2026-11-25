import os
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate

from dotenv import load_dotenv
#Load Environment Variables
load_dotenv()


def main():

    print("Hello from first-hello-project!")
    information ="""
    Elon Musk is a South African-born American business magnate and entrepreneur best known as CEO of Tesla and founder of SpaceX. He co-founded Zip2, PayPal, OpenAI, Neuralink, and The Boring Company, acquired Twitter (rebranded X), and founded xAI. 
    """
    summary_template = """
    Given the information {information} about a person I want you to create:
    1. A short summary
    2. Two interesting facts about them
    """
    summary_prompt_template = PromptTemplate(
        input_variables = ["information"], template=summary_template
    )
    llm = ChatOpenAI(temperature=0, model="gpt-5")
    #llm = ChatOllama(temperature=0, model="gemma3:270m")


    chain = summary_prompt_template | llm

    response = chain.invoke(input={"information": information})
    print(response.content)
if __name__ == "__main__":
    main()
