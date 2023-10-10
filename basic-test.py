import requests
from PIL import Image
from io import BytesIO
import scrapy
from scrapy.crawler import CrawlerProcess

# Fetch an image using requests and modify it using Pillow
def fetch_and_modify_image(url):
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    
    # Make the image grayscale
    grayscale_image = image.convert("L")
    grayscale_image.show()

# Scrapy Spider to scrape quotes from http://quotes.toscrape.com
class QuoteSpider(scrapy.Spider):
    name = "quote_spider"
    start_urls = ["http://quotes.toscrape.com"]

    def parse(self, response):
        for quote in response.css("div.quote"):
            text = quote.css("span.text::text").get()
            author = quote.css("span small.author::text").get()
            print(f"{text} - {author}")

def main():
    # Fetch and show modified image
    image_url = "https://loremflickr.com/320/240"
    fetch_and_modify_image(image_url)

    # Scrape quotes using Scrapy
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })
    process.crawl(QuoteSpider)
    process.start()

if __name__ == "__main__":
    main()
