import urllib.request
try:
    urllib.request.urlopen('http://localhost:8000/api/scanner/history')
except Exception as e:
    print(e.read().decode())
