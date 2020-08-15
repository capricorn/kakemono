import json
import shutil
import re
from collections import namedtuple

import requests
from bs4 import BeautifulSoup

#ThreadMetadata = namedtuple('ThreadMetadata', 'id last_modified')
class ThreadMetadata():
    def __init__(self, id_, last_modified):
        self.id = id_
        self.last_modified = last_modified

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        return isinstance(other, ThreadMetadata) and self.id == other.id

    def __lt__(self, other):
        return isinstance(other, ThreadMetadata) and self.last_modified < other.last_modified

    def __gt__(self, other):
        return isinstance(other, ThreadMetadata) and self.last_modified > other.last_modified

    def __str__(self):
        return str(self.id)

    def __repr__(self):
        return str(self.id)

def get_board_threads(board):
    return requests.get(f'https://a.4cdn.org/{board}/threads.json').json()

def get_active_threads(board):
    threads = get_board_threads(board)
    return [ ThreadMetadata(thread['no'], thread['last_modified']) for page in threads for thread in page['threads'] ]

def get_catalog(board):
    return requests.get(f'https://a.4cdn.org/{board}/catalog.json').json()

def get_thread(board, thread_id):
    ''' Return list of post objects in thread on the given board '''
    resp = requests.get(f'https://a.4cdn.org/{board}/thread/{thread_id}.json')
    resp.raise_for_status()
    return resp.json()['posts']

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
