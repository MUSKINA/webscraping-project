import scrapy
import re
from ..items import ProductItem  # Import the ProductItem

class Carbon38Spider(scrapy.Spider):
    name = "carbon38"
    start_urls = [
        "https://carbon38.com/en-in/collections/tops?filter.p.m.custom.available_or_waitlist=1&page=1" #starting url
    ]

    def parse(self, response):
        # Extract product links from the current page
        product_links = response.css('.ProductItem__Title.Heading a::attr(href)').getall()

        # Loop through product links and follow each to get product details
        for link in product_links:
            absolute_url = response.urljoin(link)
            yield response.follow(absolute_url, callback=self.parse_product_page)

        # Handle pagination: Extract the link to the next page
        next_page = self.get_next_page(response)
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def get_next_page(self, response):
        # Extract the "Next" page link by checking the 'href' attribute in pagination
        next_page = response.css('a.Pagination__NavItem.Link.Link--primary[rel="next"]::attr(href)').get()

        # If no "Next" page link is found, return None
        if not next_page:
            # Find the "Previous" page link and modify for "Next"
            next_page = response.css('a.Pagination__NavItem.Link.Link--primary[rel="next"]::attr(href)').get()
        return next_page

    def parse_product_page(self, response):
        # Extract product details from each product page
        name = response.xpath('//h1[contains(@class, "ProductMeta__Title")]/text()').get()
        brand = response.xpath('//h2[contains(@class, "ProductMeta__Vendor")]/a/text()').get()
        price = response.xpath('//span[contains(@class, "ProductMeta__Price")]/text()').get()
        color = response.xpath('//span[contains(@class, "ProductForm__SelectedValue")]/text()').get()

        sizes, unique_sizes = self.get_sizes(response)
        primary_image_url = response.xpath(
            '//div[contains(@class, "AspectRatio") and contains(@class, "AspectRatio--withFallback")]//img/@src').get()
        image_urls = self.extract_image_urls(response)
        product_id = response.css('div[data-yotpo-product-id]::attr(data-yotpo-product-id)').get()
        description = response.xpath('//div[contains(@class, "Faq__Answer")]//p/text()').get()
        skus = self.get_skus(response)
        review_count = self.get_review_count(response)
        product_url = response.url  # Adding the product URL

        # Yield the extracted data as a ProductItem
        item = ProductItem(
            product_name=name,
            brand=brand,
            price=price,
            color=color,
            sizes=unique_sizes,
            primary_image_url=primary_image_url,
            image_urls=image_urls,
            product_id=product_id,
            description=description,
            review=review_count,
            sku=skus,
            product_url=product_url  # Adding product URL
        )

        yield item

    def get_sizes(self, response):
        sizes = response.xpath(
            '//li[contains(@class, "HorizontalList__Item")]//label[@class="SizeSwatch"]/text()').getall()
        unique_sizes = list(set([size.strip() for size in sizes if size.strip()]))
        return sizes, unique_sizes

    def extract_image_urls(self, response):
        srcset = response.xpath(
            '//div[contains(@class, "AspectRatio") and contains(@class, "AspectRatio--withFallback")]//img/@srcset').get()
        if srcset:
            return [url.split(' ')[0] for url in srcset.split(',')]
        return []

    def get_skus(self, response):
        skus = response.xpath('//select[@id and @name="id"]/option/@data-sku').getall()
        base_skus = {self.clean_sku(sku.strip()) for sku in skus if sku.strip()}
        return list(base_skus)

    def clean_sku(self, sku):
        if '-' in sku:
            sku = '-'.join(sku.split('-')[:-1])
        return sku

    def get_review_count(self, response):
        reviews_text = response.xpath(
            '//div[@class="yotpo-bottom-line-summary"]//div[contains(@class, "yotpo-bottom-line-score")]/text()').get()
        if reviews_text:
            match = re.search(r'(\d+)', reviews_text)
            if match:
                return int(match.group(1))
        return 0
