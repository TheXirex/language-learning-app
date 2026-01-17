import json
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

        selector = response.css('div.pos-body') or response.css('span.idiom-body')
        
        def_blocks = selector.css('div.def-block.ddef_block') if selector else []
        
        word_data['word'] = response.css('div.di-title *::text').get()
        
        # TODO: check css for all keys in definition_data
        for def_block in def_blocks:
            definition_data = {
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


def run_spider(word):

    result = dict()
    
    def collect_item(item):
        nonlocal result
        result = dict(item)
    
    process = CrawlerProcess(settings=SCRAPPER_SETTINGS)
    
    crawler = process.create_crawler(CambridgeDictionarySpider)
    crawler.signals.connect(collect_item, signal=scrapy.signals.item_scraped)
    process.crawl(crawler, word=word)
    process.start()
    
    return result


if __name__ == "__main__":
    test_words = 'hard'
    
    result = run_spider(test_words)
    
    word = result.get('word', 'unknown')

    with open('output/result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)