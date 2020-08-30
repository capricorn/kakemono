import asyncio
from collections import namedtuple
import json

import redis
from requests.exceptions import HTTPError

import fourchan
import webm_extractor as extractor

#WebmEntry = namedtuple('WebmEntry', 'id last_modified urls')
class WebmEntry(fourchan.ThreadMetadata):
    def __init__(self, board, thread_id, title, webm_urls):
        self.board = board
        self.id = thread_id
        self.title = title
        self.urls = webm_urls

    '''
    def __init__(self, thread_metadata, webm_urls):
        super().__init__(thread_metadata.id, thread_metadata.last_modified)
        self.urls = webm_urls
    '''

async def extract_thread_webms_task(db, queue):
    print('Extraction worker task started')

    while True:
        board, thread_metadata = await queue.get()
        key = f'{board}.{thread_metadata.id}'
        print(f'Handling extraction for {key}')

        # switch to aiohttp
        try:
            thread = fourchan.get_thread(board, thread_metadata.id)
            webm_urls = [ f'https://i.4cdn.org/{board}/{post["tim"]}.webm' for post in extractor.get_webm_posts(thread) ]

            if 'archived' in thread[0] and thread[0]['archived'] == 1:
                print('Removing archived thread')
                db.delete(key)
            else:
                # Guess we could just re-set the key.. (can later reload as json)
                print('Setting keys for thread')
                db.set(
                    key, 
                    json.dumps(
                        WebmEntry(
                            board, 
                            thread_metadata.id, 
                            thread[0]['sub'] if 'sub' in thread[0] else '', 
                            webm_urls
                        ).__dict__
                    )
                )

        except HTTPError:
            print('Removing 404\'d thread')
            db.delete(key)
        finally:
            queue.task_done()
            await asyncio.sleep(1)

# Need to place queue jobs for all current threads for initializing redis
async def init_catalog(queue, board, catalog):
    # Start with a blank, fresh db? (flushdb command)
    # could also print out time in seconds to complete

    print('Initializing webm catalog')
    print(f'Placing {len(catalog)} extraction tasks')
    [ queue.put_nowait((board, thread_id)) for thread_id in catalog ]
    await queue.join()

async def main():
    db = redis.Redis()
    # Switch return object to thread?
    board = 'wsg'
    # On first run, also need to initialize redis with all of the threads..
    # Produce a working task list..
    prev_threads = fourchan.get_active_threads(board)
    job_queue = asyncio.Queue()

    # Spin up worker task here
    asyncio.create_task(extract_thread_webms_task(db, job_queue))

    await init_catalog(job_queue, board, prev_threads)
    print('Finished initializing catalog.')

    while True:
        await asyncio.sleep(30)
        print('Checking catalog for changes')
        #curr_threads = set(fourchan.get_active_threads(board))
        curr_threads = fourchan.get_active_threads(board)

        # XOR of threads indicates either thread is deleted, or thread is new.
        # If it's new, key needs added. Old, key needs deleted.. so this could work.
        catalog_delta = set(curr_threads) ^ set(prev_threads)
        if catalog_delta != set():
            print(f'Adding {len(catalog_delta)} thread extraction tasks')
            [ job_queue.put_nowait((board, thread)) for thread in catalog_delta ]

        # Need to also check threads if their last_modified is different from
        # those that are on record
        # (Basically, find all identical pairs where last_modified has changed)

        prev_thread_map = { thread.id: thread for thread in prev_threads }

        updated_threads = [ 
            thread for thread in curr_threads 
            if ((thread.id in prev_thread_map) and (thread > prev_thread_map[thread.id]))
        ]

        if len(updated_threads) > 0:
            print(updated_threads)
            print(f'Updating {len(updated_threads)} threads')
            [ job_queue.put_nowait((board, thread)) for thread in updated_threads ]

        prev_threads = curr_threads

''' Responsible for updating the redis db w/ current threads & webms '''
if __name__ == '__main__':
    asyncio.run(main())
