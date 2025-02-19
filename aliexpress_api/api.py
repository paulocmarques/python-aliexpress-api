"""AliExpress API wrapper for Python

A simple Python wrapper for the AliExpress Open Platform API. This module allows
to get product information and affiliate links from AliExpress using the official
API in an easier way.
"""

from aliexpress_api.errors.exceptions import CategoriesNotFoudException
from aliexpress_api.helpers.categories import filter_child_categories, filter_parent_categories
from aliexpress_api.models.category import ChildCategory
from .skd import setDefaultAppInfo
from .skd import api as aliapi
from .errors import ProductsNotFoudException, InvalidTrackingIdException, OrdersNotFoundException
from .helpers import api_request, parse_products, get_list_as_string, get_product_ids
from . import models

from typing import List, Union


class AliexpressApi:
    """Provides methods to get information from AliExpress using your API credentials.

    Args:
        key (str): Your API key.
        secret (str): Your API secret.
        language (str): Language code. Defaults to EN.
        currency (str): Currency code. Defaults to USD.
        tracking_id (str): The tracking id for link generator. Defaults to None.
    """

    def __init__(self,
        key: str,
        secret: str,
        language: models.Language,
        currency: models.Currency,
        tracking_id: str = None,
        app_signature: str = None,
        **kwargs):
        self._key = key
        self._secret = secret
        self._tracking_id = tracking_id
        self._language = language
        self._currency = currency
        self._app_signature = app_signature
        self.categories = None
        setDefaultAppInfo(self._key, self._secret)


    def get_products_details(self,
        product_ids: Union[str, List[str]],
        fields: Union[str, List[str]] = None,
        country: str = None,
        **kwargs) -> List[models.Product]:
        """Get products information.

        Args:
            product_ids (``str | list[str]``): One or more links or product IDs.
            fields (``str | list[str]``): The fields to include in the results. Defaults to all.
            country (``str``): Filter products that can be sent to that country. Returns the price
                according to the country's tax rate policy.

        Returns:
            ``list[models.Product]``: A list of products.

        Raises:
            ``ProductsNotFoudException``
            ``InvalidArgumentException``
            ``ApiRequestException``
            ``ApiRequestResponseException``
        """
        product_ids = get_product_ids(product_ids)
        product_ids = get_list_as_string(product_ids)

        request = aliapi.rest.AliexpressAffiliateProductdetailGetRequest()
        request.app_signature = self._app_signature
        request.fields = get_list_as_string(fields)
        request.product_ids = product_ids
        request.country = country
        request.target_currency = self._currency
        request.target_language = self._language
        request.tracking_id = self._tracking_id

        response = api_request(request, 'aliexpress_affiliate_productdetail_get_response')

        if response.current_record_count > 0:
            response = parse_products(response.products.product)
            return response
        else:
            raise ProductsNotFoudException('No products found with current parameters')


    def get_affiliate_links(self,
        links: Union[str, List[str]],
        link_type: models.LinkType = models.LinkType.NORMAL,
        **kwargs) -> List[models.AffiliateLink]:
        """Converts a list of links in affiliate links.

        Args:
            links (``str | list[str]``): One or more links to convert.
            link_type (``models.LinkType``): Choose between normal link with standard commission
                or hot link with hot product commission. Defaults to NORMAL.

        Returns:
            ``list[models.AffiliateLink]``: A list containing the affiliate links.

        Raises:
            ``InvalidArgumentException``
            ``InvalidTrackingIdException``
            ``ProductsNotFoudException``
            ``ApiRequestException``
            ``ApiRequestResponseException``
        """
        if not self._tracking_id:
            raise InvalidTrackingIdException('The tracking id is required for affiliate links')

        links = get_list_as_string(links)

        request = aliapi.rest.AliexpressAffiliateLinkGenerateRequest()
        request.app_signature = self._app_signature
        request.source_values = links
        request.promotion_link_type = link_type
        request.tracking_id = self._tracking_id

        response = api_request(request, 'aliexpress_affiliate_link_generate_response')

        if response.total_result_count > 0:
            return response.promotion_links.promotion_link
        else:
            raise ProductsNotFoudException('Affiliate links not available')


    def get_hotproducts(self,
        category_ids: Union[str, List[str]] = None,
        delivery_days: int = None,
		fields: Union[str, List[str]] = None,
		keywords: str = None,
		max_sale_price: int = None,
		min_sale_price: int = None,
		page_no: int = None,
		page_size: int = None,
		platform_product_type: models.ProductType = None,
		ship_to_country: str = None,
		sort: models.SortBy = None,
        **kwargs) -> models.HotProductsResponse:
        """Search for affiliated products with high commission.

        Args:
            category_ids (``str | list[str]``): One or more category IDs.
            delivery_days (``int``): Estimated delivery days.
            fields (``str | list[str]``): The fields to include in the results list. Defaults to all.
            keywords (``str``): Search products based on keywords.
            max_sale_price (``int``): Filters products with price below the specified value.
                Prices appear in lowest currency denomination. So $31.41 should be 3141.
            min_sale_price (``int``): Filters products with price above the specified value.
                Prices appear in lowest currency denomination. So $31.41 should be 3141.
            page_no (``int``):
            page_size (``int``): Products on each page. Should be between 1 and 50.
            platform_product_type (``models.ProductType``): Specify platform product type.
            ship_to_country (``str``): Filter products that can be sent to that country.
                Returns the price according to the country's tax rate policy.
            sort (``models.SortBy``): Specifies the sort method.

        Returns:
            ``models.HotProductsResponse``: Contains response information and the list of products.

        Raises:
            ``ProductsNotFoudException``
            ``ApiRequestException``
            ``ApiRequestResponseException``
        """
        request = aliapi.rest.AliexpressAffiliateHotproductQueryRequest()
        request.app_signature = self._app_signature
        request.category_ids = get_list_as_string(category_ids)
        request.delivery_days = str(delivery_days)
        request.fields = get_list_as_string(fields)
        request.keywords = keywords
        request.max_sale_price = max_sale_price
        request.min_sale_price = min_sale_price
        request.page_no = page_no
        request.page_size = page_size
        request.platform_product_type = platform_product_type
        request.ship_to_country = ship_to_country
        request.sort = sort
        request.target_currency = self._currency
        request.target_language = self._language
        request.tracking_id = self._tracking_id

        response = api_request(request, 'aliexpress_affiliate_hotproduct_query_response')

        if response.current_record_count > 0:
            response.products = parse_products(response.products.product)
            return response
        else:
            raise ProductsNotFoudException('No products found with current parameters')


    def get_products(self,
        category_ids: Union[str, List[str]] = None,
        delivery_days: int = None,
		fields: Union[str, List[str]] = None,
		keywords: str = None,
		max_sale_price: int = None,
		min_sale_price: int = None,
		page_no: int = None,
		page_size: int = None,
		platform_product_type: models.ProductType = None,
		ship_to_country: str = None,
		sort: models.SortBy = None,
        **kwargs) -> models.ProductsResponse:
        """Search for affiliated products.

        Args:
            category_ids (``str | list[str]``): One or more category IDs.
            delivery_days (``int``): Estimated delivery days.
            fields (``str | list[str]``): The fields to include in the results list. Defaults to all.
            keywords (``str``): Search products based on keywords.
            max_sale_price (``int``): Filters products with price below the specified value.
                Prices appear in lowest currency denomination. So $31.41 should be 3141.
            min_sale_price (``int``): Filters products with price above the specified value.
                Prices appear in lowest currency denomination. So $31.41 should be 3141.
            page_no (``int``):
            page_size (``int``): Products on each page. Should be between 1 and 50.
            platform_product_type (``models.ProductType``): Specify platform product type.
            ship_to_country (``str``): Filter products that can be sent to that country.
                Returns the price according to the country's tax rate policy.
            sort (``models.SortBy``): Specifies the sort method.

        Returns:
            ``models.ProductsResponse``: Contains response information and the list of products.

        Raises:
            ``ProductsNotFoudException``
            ``ApiRequestException``
            ``ApiRequestResponseException``
        """
        request = aliapi.rest.AliexpressAffiliateProductQueryRequest()
        request.app_signature = self._app_signature
        request.category_ids = get_list_as_string(category_ids)
        request.delivery_days = str(delivery_days)
        request.fields = get_list_as_string(fields)
        request.keywords = keywords
        request.max_sale_price = max_sale_price
        request.min_sale_price = min_sale_price
        request.page_no = page_no
        request.page_size = page_size
        request.platform_product_type = platform_product_type
        request.ship_to_country = ship_to_country
        request.sort = sort
        request.target_currency = self._currency
        request.target_language = self._language
        request.tracking_id = self._tracking_id

        response = api_request(request, 'aliexpress_affiliate_product_query_response')

        if response.current_record_count > 0:
            response.products = parse_products(response.products.product)
            return response
        else:
            raise ProductsNotFoudException('No products found with current parameters')


    def get_categories(self, **kwargs) -> List[Union[models.Category, ChildCategory]]:
        """Get all available categories, both parent and child.

        Returns:
            ``list[models.Category | models.ChildCategory]``: A list of categories.

        Raises:
            ``CategoriesNotFoudException``
            ``ApiRequestException``
            ``ApiRequestResponseException``
        """
        request = aliapi.rest.AliexpressAffiliateCategoryGetRequest()
        request.app_signature = self._app_signature

        response = api_request(request, 'aliexpress_affiliate_category_get_response')

        if response.total_result_count > 0:
            self.categories = response.categories.category
            return self.categories
        else:
            raise CategoriesNotFoudException('No categories found')


    def get_parent_categories(self, use_cache=True, **kwargs) -> List[models.Category]:
        """Get all available parent categories.

        Args:
            use_cache (``bool``): Uses cached categories to reduce API requests.

        Returns:
            ``list[models.Category]``: A list of parent categories.

        Raises:
            ``CategoriesNotFoudException``
            ``ApiRequestException``
            ``ApiRequestResponseException``
        """
        if not use_cache or not self.categories:
            self.get_categories()
        return filter_parent_categories(self.categories)


    def get_child_categories(self, parent_category_id: int, use_cache=True, **kwargs) -> List[models.ChildCategory]:
        """Get all available child categories for a specific parent category.

        Args:
            parent_category_id (``int``): The parent category id.
            use_cache (``bool``): Uses cached categories to reduce API requests.

        Returns:
            ``list[models.ChildCategory]``: A list of child categories.

        Raises:
            ``CategoriesNotFoudException``
            ``ApiRequestException``
            ``ApiRequestResponseException``
        """
        if not use_cache or not self.categories:
            self.get_categories()
        return filter_child_categories(self.categories, parent_category_id)


    def smart_match_product(self,
            device_id: str,
            app: str = None,
            country: str = None,
            device: str = None,
            fields: Union[str, List[str]] = None,
            keywords: str = None,
            page_no: int = None,
            product_id: str = None,
            site: str = None,
            target_currency: str = None,
            target_language: str = None,
            tracking_id: str = None,
            user: str = None,
            **kwargs) -> models.HotProductsResponse:
        """
        Get affiliated products using smart match based on keyword and device information.

        Args:
            country (``str``): Country code for target location.
            device (``str``): Device type for targeting (e.g., "mobile", "desktop").
            device_id (``str``): Unique device ID.
            fields (``str | list[str]``): Fields to include in the results list. Defaults to all.
            keywords (``str``): Search products based on keywords.
            page_no (``int``): Page number of results to fetch.
            product_id (``str``): Specific product ID to match (optional).
            site (``str``): Site information for product targeting.
            target_currency (``str``): Currency code for prices (default is EUR).
            target_language (``str``): Language code for results (default is ES).
            tracking_id (``str``): Affiliate tracking ID for results.
            user (``str``): User identifier for additional targeting (optional).

        Returns:
            ``models.ProductSmartmatchResponse``: Contains response information and the list of products.

        Raises:
            ``ProductsNotFoundException``
            ``ApiRequestException``
            ``ApiRequestResponseException``
        """
        request = aliapi.rest.AliexpressAffiliateProductSmartmatchRequest()
        request.app = app,
        request.app_signature = self._app_signature
        request.country = country
        request.device = device
        request.device_id = device_id
        request.fields = get_list_as_string(fields)
        request.keywords = keywords
        request.page_no = page_no
        request.product_id = product_id
        request.site = site
        request.target_currency = target_currency
        request.target_language = target_language
        request.tracking_id = tracking_id
        request.user = user

        response = api_request(request, 'aliexpress_affiliate_product_smartmatch_response')

        if hasattr(response, 'products') and response.products:
            response.products = parse_products(response.products.product)
            return response
        else:
            raise ProductsNotFoudException('No products found with current parameters')
        
    def get_order_list(self,
                       status: str,
                       start_time: str,
                       end_time: str,
                       fields: Union[str, List[str]] = None,
                       locale_site: str = None,
                       page_no: int = None,
                       page_size: int = None,
                       **kwargs) -> models.OrderListResponse:
        """
        Retrieve a list of affiliate orders from AliExpress.

        Args:
            start_time (str): Start time in format 'YYYY-MM-DD HH:MM:SS'.
            end_time (str): End time in format 'YYYY-MM-DD HH:MM:SS'.
            fields (str | list[str]): The fields to include in the results list.
            locale_site (str): Locale site, such as 'ru_site' for the Russian site.
            page_no (int): Page number to fetch.
            page_size (int): Number of records per page, up to 50.
            status (str): Status filter for the orders, e.g., 'Payment Completed'.

        Returns:
            OrderListResponse: Contains response information and the list of orders.

        Raises:
            ProductsNotFoundException: If no orders are found for the specified parameters.
            ApiRequestException: If the API request fails.
        """
        request = aliapi.rest.AliexpressAffiliateOrderListRequest()
        request.app_signature = self._app_signature
        request.start_time = start_time
        request.end_time = end_time
        request.fields = ','.join(fields) if isinstance(fields, list) else fields
        request.locale_site = locale_site
        request.page_no = page_no
        request.page_size = page_size
        request.status = status

        response = api_request(request, 'aliexpress_affiliate_order_list_response')

        if response.current_record_count > 0:
            return response
        else:
            raise OrdersNotFoundException("No orders found for the specified parameters")


