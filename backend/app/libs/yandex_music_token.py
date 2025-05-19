import requests
import uuid

def get_token(login: str, password: str) -> str:
    url = "https://oauth.mobile.yandex.net/1/token"
    data = {
        "grant_type": "password",
        "client_id": "23cabbbdc0e9d8d0fc635d0c5b932d16",
        "client_secret": "53bc752bcf9e4a08a118e51fe9203300",
        "username": login,
        "password": password,
        "device_id": str(uuid.uuid4()),
        "device_name": "orbitune"
    }
    resp = requests.post(url, data=data)
    if resp.status_code != 200:
        raise Exception(f"Yandex auth failed: {resp.text}")
    return resp.json()["access_token"]
