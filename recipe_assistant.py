import os
from openai import OpenAI
from personalities import personalities


# constants
EXIT = "exit"
CHANGE = "change"


class RecipeAssistant:
    def __init__(self, model="gpt-3.5-turbo"):
        self.client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
        )
        self.personalities = personalities
        self.model = model
        self.messages = []

    def _process_user_input(self):
        user_input = input()
        print("")
        if user_input == "":
            self._process_user_input()
        if user_input == EXIT:
            self._say_goodbye()
            exit()
        elif user_input == CHANGE:
            self.messages = []  # reset prompts
            self._list_personalities()
            self._select_personality()
            self._set_system_prompts()
            self._say_introduction()
        else:
            self.messages.append({
                "role": "user",
                "content": user_input
            })
            self._process_stream()
            print("")

    def _say_introduction(self):
        self.messages.append({
            "role": "user",
            "content": "Hi! Please introduce yourself. Explain who you are, your personality traits, and how you can help me."
        })
        self._process_stream()
        print("")

    def _say_goodbye(self):
        self.messages.append({
            "role": "user",
            "content": "I'm exiting out of the program now. Can you say goodbye in a way that matches your personality?"
        })
        self._process_stream()
        print("")

    def _list_personalities(self):
        print("Available helpers:")
        for i, personality in enumerate(self.personalities, 1):
            print(f"    {i}. {personality.get('summary')}")
        print("")

    def _select_personality(self):
        digit = input(f"Who would you like help from (enter a number between 1-{len(self.personalities)})? ")
        print()
        try:
            index = int(digit) - 1
            if 0 <= index < len(self.personalities):
                self.selected_option = self.personalities[index]
                print(f"Selected helper: {self.selected_option.get('summary')}\n")
            else:
                print(f"Invalid helper. Please enter a number between 1-{len(self.personalities)}.")
                self._select_personality()
        except ValueError:
            print(f"Invalid helper. Please enter a number between 1-{len(self.personalities)}.")
            self._select_personality()

    def _process_stream(self):
        collected_messages = []
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            stream=True,
        )
        for chunk in stream:
            chunk_message = chunk.choices[0].delta.content or ""
            print(chunk_message, end="")
            collected_messages.append(chunk_message)
        self.messages.append({
            "role": "system",
            "content": "".join(collected_messages)
        })

    def _set_system_prompts(self):
        self.messages = [
            {
                "role": "system",
                "content": self.selected_option.get('prompt'),
            },
            {
                "role": "system",
                "content":
                    "You are an experienced chef that helps people by suggesting detailed recipes for dishes they want to cook. "
                    "You can also provide tips and tricks for cooking and food preparation. "
                    "You always try to be as clear as possible and provide the best possible recipes for the user's needs. "
                    "You know a lot about different cuisines and cooking techniques. "
                    "You are also very patient and understanding with the user's needs and questions.",
            },
            {
                "role": "system",
                "content":
                    "Your client is going to provide one of three possible inputs: suggesting dishes based on ingredients, giving recipes to dishes, or criticizing the recipes given by the client's input."
                    "If the client passes a different prompt than these three scenarios as the first message, you should politely deny the request and clarify to the client what type of inputs you support. "
                    "If the client passes one or more ingredients, you should suggest a dish name that can be made with these ingredients. In this scenario, please only provide the dish name only and do not include ingredients for the suggested dish. "
                    "If the client passes a dish name, you should give a recipe for that dish. If you do not recognize the dish, you "
                    "should not try to generate a recipe for it. Do not answer a recipe if you do not understand the name of "
                    "the dish. If you know the dish, you must answer directly with a detailed recipe for it. If you don't know "
                    "the dish, you should answer that you don't know the dish and end the conversation."
                    "If the user passes a recipe for a dish, you should criticize the recipe and suggest changes"
            },
            {
                "role": "system",
                "content":
                    "You are one member in a list of helpers with very different personalities. "
                    "You may be switched to a new helper at the users request. "
                    f"If the user inputs '{CHANGE}' as the only word they will swap to a new user. "
                    f"If the user inputs '{EXIT}' as the only word, they will exit the program. "
                    f"After you suggest a dish or recipe, please remind the user they may input the word '{CHANGE}' and '{EXIT}'."
            }
        ]

    def chat(self):
        print('Welcome to your new favorite cooking tool! Our digital helpers can suggest delicious dishes based on ingredients and give you instructions on how to make your favorite dishes. They all come with a unique personality as well ;). To get started, please select your helper!\n')

        self._list_personalities()
        self._select_personality()
        self._set_system_prompts()
        self._say_introduction()

        while True:
            self._process_user_input()
