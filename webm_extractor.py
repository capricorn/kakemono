from collections import namedtuple

from jinja2 import Template

import fourchan

WebmThread = namedtuple('WebmThread', 'thread_url webm_url thread_title')

def get_webm_threads(board, raw_threads):
    webms = [ 
        WebmThread(
            f'https://a.4cdn.org/{board}/thread/{post["no"]}.json',
            f'https://i.4cdn.org/{board}/{post["tim"]}.webm',
            (post['sub'] if 'sub' in post else '')
        ) 

        for post in posts if ('ext' in post and post['ext'] == '.webm') 
    ]

    return webms

catalog = fourchan.get_catalog('wsg')

# Really should put in fourchan library (or find an official one instead)
posts = []
for page in catalog:
    posts.extend(page['threads'])


webms = get_webm_threads('wsg', posts)

with open('webm_template.html') as template:
    print(Template(template.read()).render(webms=webms[:6]))
