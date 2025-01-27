import requests

config = {}
with open('.config', 'r') as f:
    for line in f:
        key, value = line.strip().split('=')
        config[key] = value

headers = {
    'X-Figma-Token': config["FIGMA_TOKEN"]
}

response = requests.get(f'https://api.figma.com/v1/files/{config["FILE_KEY"]}', headers=headers)

if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print('Error:', response.status_code, response.text)
