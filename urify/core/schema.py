from pydantic import BaseModel, root_validator, validator
from typing import Optional, TypeAlias


Url: TypeAlias = str
Filter: TypeAlias = set[str] | tuple[str, ...] | list[str] | None

class UrlError(Exception):
    """Custom Url Exception"""
    ...


class QueryObject(BaseModel):
    """Interface defining query components"""
    key: str
    value: str


class UrlObject(BaseModel):

    """
    Interface defining various components of a Url

    :param scheme: scheme component. for example: http, https, etc.
    :param username: username component.
    :param password: password component.
    :param subdomain: subdomain component. for example: forums, blog, etc.
    :param domain: domain component. for example: google, facebook, etc.
    :param tld: tld component. for example: com, onion, co.in, gov, etc.
    :param port: port component. for example: 8080, 80, 443, etc.
    :param path: path component. for example: /about, /blog.html, /index.php, etc.
    :param raw_query: raw query component. for example: id=123, page=10, etc.
    :param query: jsonified query component. for example: [{key: "id", value: "123"}], etc.
    :param fragment: fragment component. for example: #team, #contact-us
    :param apex: registered domain component. for example: github.com, isro.gov.in, etc.
    :param fqdn: fully qualified domain name component. for example: chat.openai.com, etc.
    """

    scheme: str 
    username: Optional[str] 
    password: Optional[str]
    subdomain: str 
    domain: str 
    tld: str 
    port: Optional[str | int]
    path: str
    raw_query: str 
    query: list[QueryObject]
    fragment: str 
    apex: Url
    fqdn: Url
    
    class Config:
        arbitrary_types_allowed = True

    @validator('port', pre=True)
    @classmethod
    def stringify_port(cls, port):
        if isinstance(port, int):
            port = str(port)
        return port

    @property
    def keys(self):
        """List of keys present in the raw query"""
        if not self.query:
            return None
        return [obj.key for obj in self.query]

    @property
    def values(self):
        """List of values present in the raw query"""
        if not self.query:
            return None
        return [obj.value for obj in self.query]
    
    @property
    def params(self):
        if not self.raw_query:
            return None        
        return self.raw_query.split('&')
    
    @property
    def json(self):
        return self.model_dump_json()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({', '.join([f'{k}={v!r}' for k, v in self.__dict__.items()])})"



class UrlFilters(BaseModel):
    
    """
    Interface defining comprehensive set of filter parameters which can be applied to instances of the `Url` class.

    By default, it processes filter sets in whitelist mode, meaning that only URLs which align with the provided filter criteria are allowed through. 
    However, this behavior can be inverted to blacklist mode by setting the `as_denylist` flag to `True`.
    
    :param schemes: schemes to be filtered. for example: http, https, etc.
    :param subdomains: subdomains to be filtered. for example: forums, blog, etc.
    :param domains: domains to be filtered. for example: google, facebook, etc.
    :param tlds: tlds to be filtered. for example: com, onion, co.in, gov, etc.
    :param ports: port numbers to be filtered. for example: 8080, 80, 13306, etc.
    :param extensions: extensions to be filtered. for example: .jpg, .php, .html, etc.
    :param apexes: registered domains to be filtered. for example: github.com, isro.gov.in, etc.
    :param fqdns: fully qualified domain names to be filtered. for example: chat.openai.com, etc.

    :param as_denylist: when set to true, filters are processed as a blacklist
    """

    schemes: Filter = None
    subdomains: Filter = None
    domains: Filter = None
    tlds: Filter = None
    ports: Filter = None
    extensions: Filter = None
    apexes: Filter = None
    fqdns: Filter = None
    as_denylist: bool = False

    @root_validator(pre=True)
    def validate_fields(cls, values: dict):
        extensions = values.pop('extensions')
        if extensions:
            extensions = {
                f".{ext.strip('.')}" for ext in extensions
            }
        state = values.pop('as_denylist')
        for v in values.values():
            if v is None or isinstance(v, set):
                continue
            v = set(v)

        return {
            **values, 'extensions': extensions, 'as_denylist': state
        }