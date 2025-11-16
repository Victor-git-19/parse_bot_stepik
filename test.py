import json
import requests

resp = requests.get("https://stepik.org/api/users/213662538")
resp.raise_for_status()  # optional, but surfaces errors early
data = resp.json()       # parse response to Python dict

print(json.dumps(data, ensure_ascii=False, indent=2))
