from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")


def call_ai():
    try:
        client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")
    except Exception as e:
        print(f"ERROR WHILE INITIALIZING CLIENT:{e}")
        return
    print("Hi!! How can i help you?")
    while True:
        print("\n")
        user_input = input(">> ").strip()
        if user_input == "//exit":
            break
        elif user_input == "//help":
            print("//exit : quit the conversation")
            print("//help : show this help message")
        else:
            try:
                res = client.chat.completions.create(
                    model = "openrouter/free",
                    messages = [{"role":"user","content":user_input}],
                )
            except Exception as e:
                print(f"ERROR WHILE FETCHING AI RESPONSE: {e}")
                return
            response = res.choices[0].message.content
            print(f"AI: {response}")

call_ai()
            

