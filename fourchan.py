import json
import shutil
import re

import requests
from bs4 import BeautifulSoup

def get_board_threads(board):
    return requests.get(f'https://a.4cdn.org/{board}/threads.json').json()

def get_active_threads(board):
    threads = get_board_threads(board)
    return [ thread['no'] for page in threads for thread in page['threads'] ]

def get_catalog(board):
    return requests.get(f'https://a.4cdn.org/{board}/catalog.json').json()

def get_thread(board, thread_id):
    return requests.get(f'https://a.4cdn.org/{board}/thread/{thread_id}.json').json()['posts']

def download_file(board, url, filename):
    print(f'Downloading file: {filename} from {url}')
    with requests.get(f'https://i.4cdn.org/{board}/{url}.webm', stream=True) as req:
        with open(filename + '.webm', 'wb') as f:
            shutil.copyfileobj(req.raw, f)

# API does not easily let us see all replies to a post.
# Returns a hashtable containing the post id, and a list of ids as replies.
def post_replies(thread):
    replies = { post['no']: [] for post in thread['posts'] }

    for post in thread['posts']:
        if 'com' in post and post['com']:
            parser = BeautifulSoup(post['com'], 'html.parser')
            for reply in parser.find_all(href=re.compile('#p\d+')):
                reply_id = int(reply['href'][2:])
                replies[reply_id].append(int(post['no']))

    return replies
