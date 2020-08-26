from telegraph import Telegraph
from constants import telegraph_token

tg = Telegraph(telegraph_token)


def create_post(title, text):
    response = tg.create_page(title=title, html_content=text, author_name='Word Cards Bot', author_url='https://t.me/Word_Cards_Bot')
    return f"https://telegra.ph/{response['path']}"
