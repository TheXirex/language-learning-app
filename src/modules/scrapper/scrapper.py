import multiprocessing
import scrapy
from scrapy.crawler import CrawlerProcess

from config import CEFR_LEVEL_ORDER, SCRAPPER_SETTINGS


class CambridgeDictionarySpider(scrapy.Spider):
    
    def __init__(self, word: str):
        super().__init__(name="cambridge_dictionary")
        self.word = word
        self.start_urls = [
            f"https://dictionary.cambridge.org/dictionary/english/{word.lower().replace(' ', '-')}"
        ]
    
    def parse(self, response):
        word_data = {
            'word': '',
            'url': response.url,
            'definitions': []
        }

        selector = response.css('div.pr.entry-body__el')
        
        word_data['word'] = response.css('div.di-title *::text').get()
        
        # TODO: check css for all keys in definition_data
        for dsense in response.css('div.dsense'):

            pos = dsense.css('span.pos.dsense_pos::text').get()
            guideword = dsense.css('span.guideword.dsense_gw span::text').get() or dsense.css('span.guideword.dsense_gw::text').get()
            if guideword:
                guideword = guideword.strip().strip('()')

            def_blocks = dsense.css('div.def-block.ddef_block')
            for def_block in def_blocks:
                definition_data = {
                    'pos': pos,
                    'guideword': guideword,
                    'level': def_block.css('span.epp-xref.dxref::text').get(),
                    'definition': ''.join(def_block.css('div.def.ddef_d.db').xpath('.//text()').getall()).strip(),
                    'examples': [
                        ' '.join(''.join(text_parts).split()).replace('\"', '')
                        for span in def_block.css('div.examp.dexamp span.eg.deg')
                        if (text_parts := span.xpath('.//text()').getall())
                    ]
                }

                if definition_data['definition'] is None or definition_data['examples'] is None:
                    continue
                
                word_data['definitions'].append(definition_data)
        
        # Fallback to old extraction if no dsense found
        if not word_data['definitions']:
            selector = response.css('div.pos-body') or response.css('span.idiom-body')
            def_blocks = selector.css('div.def-block.ddef_block') if selector else []
            for def_block in def_blocks:
                definition_data = {
                    'pos': None,
                    'guideword': None,
                    'level': def_block.css('span.epp-xref.dxref::text').get(),
                    'definition': ''.join(def_block.css('div.def.ddef_d.db').xpath('.//text()').getall()).strip(),
                    'examples': [
                        ' '.join(''.join(text_parts).split()).replace('\"', '')
                        for span in def_block.css('div.examp.dexamp span.eg.deg')
                        if (text_parts := span.xpath('.//text()').getall())
                    ]
                }
                if definition_data['definition'] is None or definition_data['examples'] is None:
                    continue
                word_data['definitions'].append(definition_data)

        
        word_data['definitions'].sort(key=lambda x: CEFR_LEVEL_ORDER.get(x['level'], float('inf')))
                
        yield word_data


def _crawl_worker(word: str, queue) -> None:
    result = dict()

    def collect_item(item):
        nonlocal result
        result = dict(item)

    process = CrawlerProcess(settings=SCRAPPER_SETTINGS)
    crawler = process.create_crawler(CambridgeDictionarySpider)
    crawler.signals.connect(collect_item, signal=scrapy.signals.item_scraped)
    process.crawl(crawler, word=word)
    process.start()

    queue.put(result)


def run_spider(word: str) -> dict:
    ctx = multiprocessing.get_context("spawn")
    queue = ctx.Queue()
    process = ctx.Process(target=_crawl_worker, args=(word, queue))
    process.start()
    result = queue.get()
    process.join()
    return result