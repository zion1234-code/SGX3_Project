import requests

try:
    response = requests.get("http://35.206.76.195:8046/head?count=10")
    response.raise_for_status()  # raises exception for HTTP error codes
    data = response.json()       # parse JSON response
    print(data)
except requests.exceptions.RequestException as e:
    print("Request failed:", e)
except ValueError:
    print("Response not in JSON format")

