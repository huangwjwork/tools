import json
with open('dsl/python_error.json','r') as f:
    a = f.read()
json.loads(a)