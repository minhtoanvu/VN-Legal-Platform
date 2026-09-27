import urllib.request
req = urllib.request.Request(
    'http://127.0.0.1:8000/ai/chat', 
    data=b'{"question":"xin ch\xc3\xa0o"}', 
    headers={'Content-Type': 'application/json'}
)
with urllib.request.urlopen(req) as response:
    for line in response:
        print(line.decode('utf-8').strip())
