# encoding: utf-8

import os, sys
import traceback
import json
import urllib
from workflow import Workflow3, web


def get_raw_html_for_url(url):
    res = web.get(url)
    return res.text if res.status_code == 200 else None


def get_url_for_word(word):
    return "https://dle.rae.es/" + urllib.quote(word.encode('utf-8'))


def get_word_detail_object(word):
    try:
        from rae_spider import RaeSpider
        html_raw = get_raw_html_for_url(get_url_for_word(word))
        if html_raw is None:
            return None
        # log.info('crawling for word ' + word)
        word_spider = RaeSpider(html_raw)

        return word_spider.get_def_tree()
    except Exception as e:
        log.debug(traceback.format_exc())
        log.debug("Unexpected exception")
        return {}


def main(wf):
    args = wf.args
    details = get_word_detail_object(args[0])
    # log.debug('caching: ' + args[0] + " -- " + json.dumps(details))
    # log.info(json.dumps(details, indent=2))
    wf.cache_data('details_' + args[0], details)
    
if __name__ == '__main__':
    wf = Workflow3(libraries=[os.path.abspath(os.path.join(os.path.dirname(__file__), 'lib'))])
    from pyquery import PyQuery as pq # define immediately after for global use
    log = wf.logger
    wf.run(main)