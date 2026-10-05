import urllib.request

try:
    with urllib.request.urlopen("http://localhost:8000/health") as response:
        print("Backend is running:", response.read().decode('utf-8'))
except Exception as e:
    print("Backend check:", e)

try:
    with urllib.request.urlopen("http://localhost:3000") as response:
        print("Frontend is running:", response.status)
except Exception as e:
    print("Frontend check:", e)
