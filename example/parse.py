import requests 

filepath = # Path to the file
url = "http://127.0.0.1:8008/parse/pdf"

with open(filepath, "rb") as file:
    response = requests.post(url, files={"file": file})

    if response.status_code == 200:
        context = response.json()["text"]
    else:
        raise Exception(f"Failed to parse the file: {response.text}")
