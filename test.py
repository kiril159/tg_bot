import json
response = '{\n  \"user\": {\n    \"language\": \"ru\",\n    \"email\": \"\"\n  }\n}'



#a = {"LOG": json.loads(response[response.find('{') if response.find('{')!= -1 else None :])}
a = json.loads(response)
print(a)

