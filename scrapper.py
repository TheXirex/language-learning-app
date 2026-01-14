import scrapy
from scrapy.crawler import CrawlerProcess
import json


class CambridgeDictionarySpider(scrapy.Spider):
    name = 'cambridge_spider'
    
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'ROBOTSTXT_OBEY': True,
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 1,
    }
    
    def __init__(self, words='hello', *args, **kwargs):
        super(CambridgeDictionarySpider, self).__init__(*args, **kwargs)
        self.words = [w.strip() for w in words.split(',')]
        self.start_urls = [
            f"https://dictionary.cambridge.org/dictionary/english/{word.lower()}"
            for word in self.words
        ]
    
    def parse(self, response):
        word_data = {
            'word': '',
            'url': response.url,
            'definitions': []
        }
        
        title = response.css('span.hw.dhw::text').get()
        if title:
            word_data['word'] = title.strip()
        
        pos_bodies = response.css('div.pos-body')
        
        for pos_body in pos_bodies:
            def_blocks = pos_body.css('div.def-block.ddef_block')
            
            for def_block in def_blocks:
                level = def_block.css('span.epp-xref.dxref::text').get()
                level_text = level.strip() if level else ''
                
                if not level_text:
                    continue
                
                definition_data = {'level': level_text}
                
                definition_parts = def_block.css('div.def.ddef_d.db').xpath('.//text()').getall()
                if definition_parts:
                    definition_data['definition'] = ' '.join(''.join(definition_parts).split())
                else:
                    definition_data['definition'] = ''
                
                example_spans = def_block.css('div.examp.dexamp span.eg.deg')
                examples = []
                for span in example_spans:
                    text_parts = span.xpath('.//text()').getall()
                    if text_parts:
                        full_text = ' '.join(''.join(text_parts).split())
                        examples.append(full_text)
                definition_data['examples'] = examples
                
                word_data['definitions'].append(definition_data)
        
        level_order = {'A1': 1, 'A2': 2, 'B1': 3, 'B2': 4, 'C1': 5, 'C2': 6}
        word_data['definitions'].sort(key=lambda x: level_order.get(x['level'], 99))
        
        self.log(f"Scraped {word_data['word']}: {len(word_data['definitions'])} definitions found")
        
        yield word_data


def run_spider(words):
    results = []
    
    class ResultCollectorPipeline:
        def process_item(self, item, spider):
            results.append(dict(item))
            return item
    
    process = CrawlerProcess(settings={
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'ROBOTSTXT_OBEY': True,
        'ITEM_PIPELINES': {ResultCollectorPipeline: 300},
        'LOG_LEVEL': 'INFO',
    })
    
    process.crawl(CambridgeDictionarySpider, words=words)
    process.start()
    
    return results


if __name__ == "__main__":
    test_words = 'hardweqfwqe'
    
    results = run_spider(test_words)
    
    for result in results:
        word = result.get('word', 'unknown')
        filename = f'{word}_scrapy.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
    
    with open('cambridge_scrapy_all.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
