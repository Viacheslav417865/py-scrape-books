from typing import Any

import scrapy
from scrapy.http import Response


class BooksSpiderSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/catalogue/page-1.html"]

    def parse(self, response: Response, **kwargs: Any) -> None:
        # Extract all book links from the page
        book_links = response.css("h3 a::attr(href)").getall()

        # Follow each book link and scrape data
        for link in book_links:
            yield response.follow(link, self.parse_book)

        # Get the link to the next page, if available
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_book(self, response: Response) -> None:
        # Extract book information from the book detail page

        # Safely extract the title
        title = response.css("h1::text").get()

        # Safely extract price, and handle missing value
        price = response.css("p.price_color::text").get()

        # Safely extract amount in stock, handling missing data
        amount_in_stock = response.css("p.in_stock span::text").get()
        if amount_in_stock:
            amount_in_stock = amount_in_stock.strip()
        else:
            amount_in_stock = "Not Available"

        # Safely extract rating (class is like "star-rating Four")
        rating = response.css("p.star-rating::attr(class)").get()
        if rating:
            rating = rating.split(" ")[-1]
        else:
            rating = "No Rating"

        # Safely extract category (breadcrumb navigation)
        category = response.css("ul.breadcrumb li:nth-child(3) a::text").get()

        # Safely extract description, might not be available
        description = response.css(
            "meta[name=\'description\']::attr(content)").get()
        if description:
            description = description.strip()
        else:
            description = "No description available"

        # Extract UPC from the table (first row, first column)
        upc = response.css("table tr:nth-child(1) td::text").get()

        # Yield a dictionary with the scraped data
        yield {
            "title": title,
            "price": price,
            "amount_in_stock": amount_in_stock,
            "rating": rating,
            "category": category,
            "description": description,
            "upc": upc,
        }
