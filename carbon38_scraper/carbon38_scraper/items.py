import scrapy

class ProductItem(scrapy.Item):
    product_name = scrapy.Field()
    brand = scrapy.Field()
    price = scrapy.Field()
    color = scrapy.Field()
    sizes = scrapy.Field()
    primary_image_url = scrapy.Field()
    image_urls = scrapy.Field()
    product_id = scrapy.Field()
    description = scrapy.Field()
    review = scrapy.Field()
    sku = scrapy.Field()
    product_url = scrapy.Field()
