import requests
from constants import voicerss_token


def synthesise(text: str) -> bytes:
    response = requests.post(url="http://api.voicerss.org", data={
        'key': voicerss_token,
        'hl': 'en-us',
        'src': text
    })
    if response.status_code == 200:
        return response.content
