import requests

r = requests.get('http://127.0.0.1/favicon.ico')
print(r.status_code, r.text)