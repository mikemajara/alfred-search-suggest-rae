import os, sys
import json
import traceback
import logging
from pyquery import PyQuery as pq

log = logging.getLogger("rae_spider")

class RaeSpider:

    results = None
    articles = None

    def __init__(self, html_raw):
        self.html_raw = html_raw
        self.d = pq(html_raw)

    def get_results(self):
        if self.results is None:
            self.results = self.d('div#resultados')
        return self.results

    def get_articles(self):
        if self.articles is None:
            self.articles = self.get_results().find('article')
        return self.articles

    def get_title_article_title(cls, article):
        return article.find('header').text or ''

    def get_etymology(cls, article):
        etymologies = article.cssselect('.n2')
        first = next(iter(etymologies), None)
        return first.text_content() if first is not None else ''
    
    def get_meanings(cls, article):
        meaning_nodes = article.find_class('j')
        meanings = [node.text_content() for node in meaning_nodes]
        return meanings if len(meanings) > 0 else ['']

    def article_to_json(cls, article):
        try:
            result = {
                "title": cls.get_title_article_title(article),
                "etymology": cls.get_etymology(article),
                "meanings": cls.get_meanings(article)
            }
            return result
        except Exception as e:
            traceback.print_exc()
            log.debug(traceback.format_exc())
            raise e
        # if result['title'] is None:
        #     log.debug(str(article))
        #     return None
        # print('obtained result for ' + result['title'].encode('utf-8'))
        # print(json.dumps(result))
        # return result

    def get_def_tree(self):
        return [
            self.article_to_json(article)
            for article in self.get_articles()
        ]


# [
#     {
#         "title": "este"
#         "etymology": "bla bla bla"
#         "meanings": [
#             'meaning 1',
#             'meaning 2'
#         ]
#     }
# ]

