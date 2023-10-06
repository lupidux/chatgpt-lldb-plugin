import openai
import sys
import os
from os import path

program_path = path.abspath(path.join(path.dirname(__file__), '..', '..'))
sys.path.insert(0, program_path)
import api_key_config

def get_from_script():
    api_key = api_key_config.OPENAI_API_KEY
    return api_key

def get_from_env(): 
    api_key = os.environ.get('OPENAI_API_KEY')
    if api_key is None:
        raise EnvironmentError("The enviroment variable OPENAI_API_KEY is not set")
    return api_key

api_key = get_from_script()
if (api_key == "YOUR_OPENAI_API_KEY"):
    try:
        api_key = get_from_env()
    except EnvironmentError as e:
        print(e)
openai.api_key = api_key


history = [{"role": "system", "content" : "Sei un gentile e utile assistente per il debugging e la correzione del codice."}]
def send_to_chatgpt(content):
    global history
    history.append({"role": "user", "content": content})

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=history
        )

        reply = completion.choices[0].message.content
        if completion and len(completion.choices) > 0:
            history.append({"role": "assistant", "content": reply})
            return reply
        
    except openai.error.AuthenticationError as e:
        print("Authentication error:", e)
    except openai.error.OpenAIError as e:
        print("OpenAI error:", e)

def retrieve_chat():
    return history
