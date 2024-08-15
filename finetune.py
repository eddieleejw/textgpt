from utils import finetune_utils
import os


if __name__ == "__main__":
    os.environ["OPENAI_API_KEY"] = input("What is your OpenAI API key?")
    finetune_utils.main()