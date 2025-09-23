from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

groq_api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=groq_api_key)

# Test models
models_to_test = [
    "llama3-8b-8192",
    "mixtral-8x7b-32768",
    "gemma-7b-it"
]

for model in models_to_test:
    try:
        print(f"\nTesting model: {model}")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What is the capital of India?"}
            ],
            temperature=0.2,
            max_tokens=100
        )
        print(f"Success! Response: {response.choices[0].message.content}")
    except Exception as e:
        print(f"Error with {model}: {str(e)}")
        if hasattr(e, 'response'):
            print(f"Status code: {e.response.status_code}")
            print(f"Response: {e.response.text}")