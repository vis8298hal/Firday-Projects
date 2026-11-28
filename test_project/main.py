from typing import Literal
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()


class SentimentResult(BaseModel):
    """Defines the Sentiment format How It needs to be displayed"""
    sentiment: Literal["positive", "negative", "neutral"] = Field(
        description="The overall sentiment of the text."
    )
    confidence: float = Field(
        description="Confidence score between 0.0 and 1.0."
    )
    reasoning: str = Field(
        description="A brief one-sentence explanation for the sentiment."
    )

def main():
    # 1. Initialize the LLM with structured output
    llm = llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    temperature=0,
    )
    structured_llm = llm.with_structured_output(SentimentResult)

    # 2. Create the prompt template
    prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert sentiment analyzer. Classify the user's text accurately."),
    ("human", "{text}")
    ])

    # 3. Combine into a chain
    chain = prompt | structured_llm
    return chain


