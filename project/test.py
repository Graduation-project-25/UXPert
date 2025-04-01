import openai

client =openai.OpenAI(api_key = "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")

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello!"}]
)

print(response.choices[0].message.content)