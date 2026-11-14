from dotenv import load_dotenv
load_dotenv()

from anthropic import Anthropic
from openai import OpenAI


# Check per Anthropic
client = Anthropic()
models = client.models.list()


# Check per OpenAI
client_openai = OpenAI()
models_openai = client_openai.models.list()

# Print the Anthropic models available with my tokens
print("~~ ANTHROPIC ~~")
for m in models.data:
    print(m.id)

for _ in range(5):
    print("%%%%%%% ======================================================================= %%%%%%%%%")

# Print the OpenAI models available with my tokens
print("~~ OpenAI ~~")
for m in models_openai.data:
    print(m.id)






