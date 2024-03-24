from recipe_assistant import RecipeAssistant
from dotenv import load_dotenv


load_dotenv()


def main():
    assistant = RecipeAssistant()
    assistant.chat()


if __name__ == "__main__":
    main()
