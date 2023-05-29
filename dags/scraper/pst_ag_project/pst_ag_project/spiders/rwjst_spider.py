import scrapy
import datetime
import re
import posixpath
from pst_ag_project.items import PostDetails
from twisted.internet.error import DNSLookupError
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import TimeoutError, TCPTimedOutError
from scrapy.crawler import CrawlerProcess

scraped_post_list = []


class RwjstspiderSpider(scrapy.Spider):
    name = "rwjstspider"
    allowed_domains = ["rewardsforjustice.net"]
    start_urls = ["http://rewardsforjustice.net/"]

    payload = "action=jet_engine_ajax&handler=get_listing&page_settings%"\
        "5Bpost_id%5D=22076&page_settings%5Bqueried_id%5D=22076%7CWP_Post&page_"\
        "settings%5Belement_id%5D=ddd7ae9&page_settings%5Bpage%5D=1&listing_type=ele"\
        "mentor&isEditMode=false&addedPostCSS%5B%5D=22078"

    headers = {
        "authority": "rewardsforjustice.net",
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-language": "en-US,en;q=0.9,my-ZG;q=0.8,my;q=0.7",
        "cache-control": "no-cache",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "cookie": "_ga=GA1.1.2132662955.1681741987; cookie_notice_accepted=true; wp-wpml_current_language=en; _ga_BPR2J8V0QK=GS1.1.1681801651.5.1.1681802357.0.0.0",
        "origin": "https://rewardsforjustice.net",
        "pragma": "no-cache",
        "referer": "https://rewardsforjustice.net/index/?jsf=jet-engine:rewards-grid&tax=crime-category:1070%2C1071%2C1073%2C1072%2C1074",
        "sec-ch-ua": '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

    url = "https://rewardsforjustice.net/index/?jsf=jet-engine%3Arewards-grid&tax=crime-category%3A1070%2C1071%2C1073%2C1072%2C1074"

    def parse(self, response):
        request = scrapy.Request(
            url=self.url,
            callback=self.parse_api,
            headers=self.headers,
            body=self.payload,
            method="POST",
            errback=self.errback_httpbin,
        )

        yield request

    def parse_api(self, response):
        """To make request and get individual urls for each post

        Args:
            response (response_object): scrapy response object

        Yields:
            response object: A json response containing all links for a particular page
        """
        base_url = self.url
        json_response = response.json()
        total_num_of_pages = json_response["data"]["filters_data"]["props"][
            "rewards-grid"
        ]["max_num_pages"]

        for page_number in range(1, total_num_of_pages + 1):
            path = f"&pagenum={page_number}"
            url = posixpath.join(base_url, path)

            yield scrapy.Request(
                url=url,
                callback=self.parse_links,
                headers=self.headers,
                body=self.payload,
                method="POST",
                errback=self.errback_httpbin,
            )

    def parse_links(self, response):
        """To make request to each post url and get page element

        Args:
            response (response_object): scrapy response object

        Yields:
            response object: A response containing page elements
        """
        json_response = response.json()
        string = json_response["data"]["html"]
        pattern = 'data-url="https://rewardsforjustice.net/rewards/.*/'
        all_links = re.findall(pattern, string)
        clean_links = list(map(lambda x: x.split('="')[1], all_links))

        for post_link in clean_links[0:2]:
            yield scrapy.Request(url=post_link, callback=self.parse_post)

    def parse_post(self, response):
        """To get datapoints from page element

        Args:
            response (response_object): scrapy response object

        Yields:
            post_details: A dictionary of scraped post details
        """
        post_details = PostDetails()
        try:
            image_div_class = response.xpath(
                "//h2[text()='Images:']//parent::div//parent::"\
                "div//following-sibling::div[starts-with(@class, 'elementor-element')]"
            ).attrib["class"]
            image_divs = response.xpath(
                f"//div[contains(@class, '{image_div_class}')]//figure"
            )
            image_urls = [element.css("img").attrib["src"] for element in image_divs]
        except KeyError:
            image_urls = None

        try:
            dob_class = response.xpath(
                "//h2[text()='Date of Birth:']//parent::div//parent::"\
                "div//following-sibling::div[starts-with(@class, 'elementor-element')]"
            ).attrib["class"]
            dob = response.xpath(
                f"//div[contains(@class, '{dob_class}')]/div/text()"
            ).get()
        except KeyError:
            dob = None

        try:
            ass_loc_class = response.xpath(
                "//h2[contains(text(),'Associated Location')]//parent::"\
                "div//parent::div//following-sibling::div[starts-with(@class, 'elementor-element')]"
            ).attrib["class"]
            ass_loc = response.xpath(
                f"//div[contains(@class, '{ass_loc_class}')]//div//div/span/text()"
            ).getall()
        except KeyError:
            ass_loc = None

        try:
            ass_org_class = response.xpath(
                "//h2[contains(text(),'Associated Organization')]//parent::"\
                "div//parent::div//following-sibling::div[starts-with(@class, 'elementor-element')]"
            ).attrib["class"]
            ass_org = response.xpath(
                f"//div[contains(@class, '{ass_org_class}')]//div/text()"
            ).get()
        except KeyError:
            try:
                ass_org_class = response.xpath(
                    "//p[contains(text(),'Associated Organization')]"
                )
                ass_org = ass_org_class.css("a::text").get()
            except Exception:
                ass_org = None

        post_details["url"] = response.url
        post_details["category"] = response.css(
            "span.jet-listing-dynamic-terms__link::text"
        ).get()
        post_details["title"] = response.css("h2::text").get()
        post_details["reward_amount"] = response.xpath(
            '//h2[contains(text(), "Up to")]/text()'
        ).get()
        post_details["associated_organization"] = ass_org
        post_details["associated_location"] = ass_loc
        post_details["about"] = response.xpath(
            "//div[@data-widget_type='theme-post-content.default']//child::div//p/text()"
        ).getall()
        post_details["image_urls"] = image_urls
        post_details["date_of_birth"] = dob

        scraped_post_list.append(post_details)
        yield post_details

    def errback_httpbin(self, failure):
        """To log API errors

        Args:
            failure: failure object
        """

        self.logger.error(repr(failure))

        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error("HttpError on %s", response.url)

        elif failure.check(DNSLookupError):
            request = failure.request
            self.logger.error("DNSLookupError on %s", request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error("TimeoutError on %s", request.url)



