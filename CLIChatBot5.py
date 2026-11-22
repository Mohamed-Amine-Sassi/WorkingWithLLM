from dotenv import load_dotenv
from openai import OpenAI
import json
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

systemMessage=[{
    "role": "system", 
   "content":"""You are a helpfull student assistant 
   ##RULES:
   -Answer no unrelated question 
   -keep the responce short
   -if the answer is a number reply with just the result 
  """},]

#Zero shots prompting :
messages1 = systemMessage

#One Shot prompting :
messages2 = systemMessage+[
  # Example
  {"role": "user", "content": "What is 12 * 8?"},
  {"role": "assistant", "content": "96"},
]


#Few Shot Prompting :
messages3 =systemMessage+ [
  # Example 1: numeric answer -> result only
  {"role": "user", "content": "What is 12 * 8?"},
  {"role": "assistant", "content": "96"},
  # Example 2: short explanation
  {"role": "user", "content": "What is a primary key in a database?"},
  {"role": "assistant", "content": "A column (or set of columns) that uniquely identifies each row in a table."},
  # Example 3: unrelated question -> refuse
  {"role": "user", "content": "Who won the World Cup in 2022?"},
  {"role": "assistant", "content": "Sorry, I can only answer student-related questions."},
  # Example 4: numeric answer again
  {"role": "user", "content": "How many bits are in a byte?"},
  {"role": "assistant", "content": "8"},
]

# Sliding window: only the last WINDOW_SIZE messages of the conversation are sent
# to the model. 7 = the new question + the 3 previous questions and their answers.
# Keep it odd so the window always starts with a question, never an answer.
# The full conversation is still saved in history.json.
WINDOW_SIZE = 7


def build_context(message_history):
    """Return the messages to send: the fixed prompt + the most recent messages."""
    conversation = message_history[len(messages2):]
    recent = conversation[-WINDOW_SIZE:]
    return messages2 + recent


def load_history():
    """Return the saved conversation, or a fresh one if there is none."""
    if os.path.exists("/home/medamine/Desktop/AI Sessions/Working With LLMs/history.json"):
        try:
            with open("/home/medamine/Desktop/AI Sessions/Working With LLMs/history.json", "r", encoding="utf-8") as f:
                saved = json.load(f)
            if isinstance(saved, list) and saved:
                return saved
        except (OSError, json.JSONDecodeError) as e:
            print(f"COULD NOT READ /home/medamine/Desktop/AI Sessions/Working With LLMs/history.json: {e}")
    return messages2.copy()


def save_history(message_history):
    """Write the whole conversation to the JSON file."""
    with open("/home/medamine/Desktop/AI Sessions/Working With LLMs/history.json", "w", encoding="utf-8") as f:
        json.dump(message_history, f, ensure_ascii=False, indent=2)



def call_ai():
    try:
        client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")
    except Exception as e:
        print(f"ERROR WHILE INITIALIZING CLIENT:{e}")
        return
    message_history = load_history()
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
            message_history.append({"role": "user", "content": user_input})
            try:
                stream = client.chat.completions.create(
                    model = "openrouter/free",
                    # Send only the sliding window, not the full history.
                    messages = build_context(message_history),
                    # Controls creativity: lower values make replies more focused and predictable.
                    temperature = 0.7,
                    # Limits the number of tokens generated in the response.
                    max_tokens = 500,
                )
            except Exception as e:
                print(f"ERROR WHILE FETCHING AI RESPONSE: {e}")
                return
            response = stream.choices[0].message.content
            message_history.append({"role": "assistant", "content": response})
            # Save after every answer, so closing the program never loses the chat.
            try:
                save_history(message_history)
            except OSError as e:
                print(f"COULD NOT SAVE HISTORY: {e}")
            print(f"AI: {response}")


if __name__ == "__main__":
    call_ai()
            

