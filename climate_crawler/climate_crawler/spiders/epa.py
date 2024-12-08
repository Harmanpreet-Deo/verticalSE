import scrapy

class EPASpider(scrapy.Spider):
    name = "epa"
    allowed_domains = ["epa.gov"]
    start_urls = [
        "https://www.epa.gov/environmental-topics",
        "https://www.epa.gov/climate-change",
        "https://www.epa.gov/science-and-technology",
    ]

    # Define keywords for climate-related URLs
    climate_keywords = [
        "climate", "environment", "energy", "pollution", "emissions",
        "sustainability", "renewable", "carbon", "adaptation",
        "mitigation", "green", "ecology", "air", "water", "land"
    ]

    custom_settings = {
        "CLOSESPIDER_PAGECOUNT": 200,
        "DEPTH_LIMIT": 3,
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "DOWNLOAD_DELAY": 1,
        "DEFAULT_REQUEST_HEADERS": {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        },
        "ROBOTSTXT_OBEY": True,
    }

    def parse(self, response):
        self.log(f"Crawling: {response.url}")
        yield {
            "url": response.url,
            "title": response.css("title::text").get(),
            "meta_description": response.css('meta[name="description"]::attr(content)').get(),
            "content": " ".join(response.css("p::text").getall()),
        }

        for link in response.css("a::attr(href)").getall():
            if link.startswith("https://www.epa.gov") or link.startswith("/"):
                if any(keyword in link.lower() for keyword in self.climate_keywords):
                    yield response.follow(link, callback=self.parse)
