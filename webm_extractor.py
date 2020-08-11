from jinja2 import Template

import fourchan

catalog = fourchan.get_catalog('wsg')

# Really should put in fourchan library (or find an official one instead)
posts = []
for page in catalog:
    posts.extend(page['threads'])

webms = [ post for post in posts if ('ext' in post and post['ext'] == '.webm' ) ]

# Work on returning an object; for now, a tuple w/ link
# to webm, + thread subject
# + any other useful information (creation date, for example)
webms_src = [ (webm['sub'] if 'sub' in webm else '', f'https://i.4cdn.org/wsg/{webm["tim"]}.webm') for webm in webms ]

with open('webm_template.html') as template:
    print(Template(template.read()).render(webms=webms_src))
