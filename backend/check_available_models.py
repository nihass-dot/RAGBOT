from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

groq_api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=groq_api_key)

try:
    # Get list of available models
    models = client.models.list()
    
    print("Available models:")
    for model in models.data:
        print(f"- {model.id}")
    
    # Test the first available model
    if models.data:
        first_model = models.data[0].id
        print(f"\nTesting first available model: {first_model}")
        
        response = client.chat.completions.create(
            model=first_model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What is the capital of India?"}
            ],
            temperature=0.2,
            max_tokens=100
        )
        print(f"Success! Response: {response.choices[0].message.content}")
    else:
        print("No models available.")
        
except Exception as e:
    print(f"Error: {str(e)}")
    if hasattr(e, 'response'):
        print(f"Status code: {e.response.status_code}")
        print(f"Response: {e.response.text}")