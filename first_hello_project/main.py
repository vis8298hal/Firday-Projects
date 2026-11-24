import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
#Load Environment Variables
load_dotenv()


def main():

    print("Hello from first-hello-project!")
    print(os.environ.get("OPENAI_API_KEY"))


if __name__ == "__main__":
    main()
