import json

from django.shortcuts import render
from django.http import HttpResponseNotFound, HttpResponse
import redis

db = redis.Redis()

def index(request, board='wsg', thread_id=None):
    if not thread_id:
        # Render the catalog -- perhaps a more optimal way than fetching
        # all the keys..?
        catalog = db.keys('*')
        webms = [ json.loads(db.get(thread)) for thread in catalog ]
        print(catalog)
        print(webms)

        #return HttpResponseNotFound('Could not find thread!')
        return render(request, 'catalog/webm_template.html', { 'webms': webms })

    # Need to handle if key doesn't exist
    thread = db.get(board + '.' + str(thread_id))
    if not thread:
        return HttpResponseNotFound('Could not find thread!')

    webms = json.loads(thread)

    return render(request, 'catalog/thread_template.html', { 'webms': webms })
