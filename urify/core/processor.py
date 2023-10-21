from pathlib import Path
from typing import Optional, Callable
from urllib.parse import urlparse, unquote_plus

from tldextract.tldextract import extract

from .schema import Url, QueryObject, UrlObject, UrlError, UrlFilters


def querydissect(query: str) -> list[QueryObject]:
    if not query:
        return []

    """Dissects raw query into key-value list"""
    kvify: Callable[[str, str], dict] = lambda k, v: QueryObject(key=k, value=v)
    return list(kvify(
        *unquote_plus(q).split('=')) for q in query.split('&')
    )


def urldissect(url: Url, silent: bool=True) -> UrlObject | None:

    """Dissects Url into components and returns it as UrlObject"""

    scheme_flag = True
    _url = url

    if not '://' in url:
        scheme_flag = False
        _url = f"http://{url}"

    parsed = urlparse(_url)

    scheme = parsed.scheme if scheme_flag else ''
    netloc = parsed.netloc
    path = parsed.path

    if not netloc:
        partitioned =  path.partition('/')
        netloc, path = partitioned[0], ''.join(partitioned[1:])

    extracted = extract(netloc)
    if not extracted.ipv4 and not extracted.suffix and not scheme:
        if silent: return None
        raise UrlError(f'failed to parse: {url!r}')
    
    query = parsed.query

    return UrlObject(
        scheme=scheme,
        username=parsed.username or '',
        password=parsed.password or '',
        subdomain=extracted.subdomain,
        domain=extracted.domain,
        tld=extracted.suffix,
        port=str(parsed.port) or '',
        path=path,
        raw_query=query,
        query=querydissect(query),
        fragment=parsed.fragment,
        apex=extracted.registered_domain,
        fqdn=extracted.fqdn
    )


def urlfilter(
    url: Url, filters: UrlFilters, absolute: bool=False, return_obj: bool=False
) -> Optional[Url | UrlObject]:
    
    """
    An efficient and versatile method for filtering url based on provided `UrlFilters` instance.  
    
    The strictness of these filters can be controlled by the `absolute` flag. If `absolute` is set to True,
    all filter conditions must be met for the URL to pass; else, the URL can pass if any single condition is met.
    
    :param url: url to be filtered
    :param filters: filters for evaluation
    :param absolute: if true, url is only returned if all filter checks are passed
    :param return_obj: if true, returns dissected object

    :returns: Url, UrlObject or None after evaluation

    Usage:

    >>> # create filter that blocks 'php' filetype and 'example' domain, all must be verified
    >>> filters = UrlFilters(
    ...     extensions={".php"}, domains={"example"}, as_denylist=True, absolute=True
    ... )
    >>> urlfilter("https://www.example.com/index.html", filters=filters) 
    >>> "https://www.example.com/index.html"
    >>> urlfilter("https://www.example.com/index.php", filters=filters)
    >>> None
    >>> urlfilter("https://www.different.com/index.php", filters=filters)
    >>> "https://www.different.com/index.php"
    """

    url_object = urldissect(url)

    filter_mappings = (
        ('schemes', url_object.scheme),
        ('subdomains', url_object.subdomain),
        ('domains', url_object.domain),
        ('tlds', url_object.tld),
        ('ports', url_object.port),
        ('extensions', Path(url_object.path).suffix),
        ('apexes', url_object.apex),
        ('fqdns', url_object.fqdn)
    )
    # print(filters)
    filter_state = []
    for attr, component in filter_mappings:
        filter_set = getattr(filters, attr)
        if not filter_set:
            continue

        if component in filter_set:
            filter_state.append(True)
        else:
            filter_state.append(False)

    if not filter_state:
        return url_object if return_obj else url
    
    all_filters = all(filter_state)
    any_filter = any(filter_state)

    if not filters.as_denylist:
        all_filters, any_filter = not all_filters, not any_filter

    if absolute and all_filters:
        return None
    elif not absolute and any_filter:
        return None    

    return url_object if return_obj else url