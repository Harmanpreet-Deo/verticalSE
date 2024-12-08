import scrapy

class IPCCSpider(scrapy.Spider):
    name = "ipcc"
    allowed_domains = ["ipcc.ch"]
    start_urls = [
        "https://www.ipcc.ch/reports/",
    ]

    # Define keywords for report-related URLs
    report_keywords = [
        "report", "assessment", "special", "synthesis", "summary",
        "methodology", "climate", "change", "adaptation", "mitigation",
        "emissions", "scenarios", "policy", "impacts", "vulnerability"
    ]

    custom_settings = {
        "CLOSESPIDER_PAGECOUNT": 200,  # Stop after crawling 200 pages
        "DEPTH_LIMIT": 3,              # Limit crawl depth to 3 levels
        "USER_AGENT": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0.0.0 Safari/537.36"
        ),
        "DOWNLOAD_DELAY": 1,           # 1-second delay between requests
        "DEFAULT_REQUEST_HEADERS": {
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;"
                "q=0.9,*/*;q=0.8"
            ),
            "Accept-Language": "en-US,en;q=0.5",
        },
        "ROBOTSTXT_OBEY": True,        # Respect robots.txt directives
    }

    def parse(self, response):
        # Log the current URL being crawled
        self.log(f"Crawling: {response.url}")

        # Extract and yield page data
        yield {
            "url": response.url,
            "title": response.css("title::text").get(),
            "meta_description": response.css(
                'meta[name="description"]::attr(content)'
            ).get(),
            "content": " ".join(response.css("p::text").getall()),  # Extract all <p> content
        }

        # Extract and follow relevant links
        for link in response.css("a::attr(href)").getall():
            # Ensure the link belongs to the allowed domain
            if link.startswith("https://www.ipcc.ch") or link.startswith("/"):
                # Filter links containing report-related keywords
                if any(keyword in link.lower() for keyword in self.report_keywords):
                    yield response.follow(link, callback=self.parse)
