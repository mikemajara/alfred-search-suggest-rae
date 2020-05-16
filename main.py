#!/usr/bin/python
# encoding: utf-8

import os
import re
import sys
import json
import urllib
from time import time

import cache
from workflow import Workflow3, web
from workflow.background import run_in_background, is_running

DISPLAY_DETAILS = True #os.getenv('MM_DISPLAY_DETAILS').isdigit() and int(os.getenv('MM_DISPLAY_DETAILS'))
# DISPLAY_THUMBNAILS = os.getenv('MM_DISPLAY_THUMBNAILS').isdigit() and int(os.getenv('MM_DISPLAY_THUMBNAILS'))

REFRESH_RATE = 1.2

URL_SEARCH_SUGGEST_GET = "https://dle.rae.es/srv/keys?q="
URL_SEARCH_GET = "https://dle.rae.es/"


def get_rae_suggestions(word):
    url = URL_SEARCH_SUGGEST_GET + urllib.quote(word.encode('utf-8'))
    return web.get(url)


def get_url_for_word(word):
    return URL_SEARCH_GET + urllib.quote(word.encode('utf-8'))


def get_details_preview(details):
    first_article = next(iter(details), None)
    if first_article is None:
        return "No details found"
    if len(first_article.get('meanings')) <= 0: 
        log.debug(json.dumps(details))
    meanings_list = first_article.get('meanings', [])
    return first_article.get('etymology', '') + " " +\
        next(iter(first_article.get('meanings', [])), '')


def main(wf):

    if DISPLAY_DETAILS:
        from pyquery import PyQuery as pq

    args = wf.args
    searchString = ' '.join(args)
    
    if (len(args) > 0):
        res = wf.cached_data(searchString, max_age=0)
        if res is None:
            res = get_rae_suggestions(searchString).json()
            wf.cache_data(searchString, res)
        
        for word in res:
            
            # defaults 
            details_str = ""

            if DISPLAY_DETAILS:
                details = wf.cached_data('details_' + word, max_age=0)
                if details is None:
                    
                    run_in_background(
                        'update_details_' + word,
                        [
                            '/usr/bin/python',
                            wf.workflowfile('update_details.py'),
                            word
                        ]
                    )
                    details_str = "Loading details... "
                    wf.rerun = REFRESH_RATE
                else:
                    details_str = get_details_preview(details)

            wf.add_item(
                icon=None,
                valid=True,
                title=word,
                arg=word,
                autocomplete=word,
                subtitle=details_str
            ).add_modifier(
                'alt', 'Check definition'
            )

    # Default option to search if no result found
    wf.add_item(
        title="Search on web",
        subtitle="Search RAE for " + " ".join(args),
        arg=get_url_for_word(searchString),
        valid=True,
    )

    # --- 
    # Send output to Alfred. You can only call this once.
    # Well, you *can* call it multiple times, but subsequent calls
    # are ignored (otherwise the JSON sent to Alfred would be invalid).
    # ----
    wf.send_feedback()


if __name__ == '__main__':
    # Create a global `Workflow3` object
    wf = Workflow3(libraries=[os.path.abspath(os.path.join(os.path.dirname(__file__), 'lib'))])
    # wf = Workflow3(libraries=[os.path.join(os.path.dirname(__file__), 'lib')])
    log = wf.logger
    # Call your entry function via `Workflow3.run()` to enable its
    # helper functions, like exception catching, ARGV normalization,
    # magic arguments etc.
    sys.exit(wf.run(main))