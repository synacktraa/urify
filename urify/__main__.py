import re
import sys
from functools import partial
from typing import Callable

try:
	from signal import signal, SIGPIPE, SIG_DFL
	signal(SIGPIPE, SIG_DFL)
except ImportError:
	pass

from .cli import Cli
from .core import schema, processor


runtime_cache = set()

def print_unique(value: str | None):
    if not value:
        return
    if value not in runtime_cache:
        print(value)
        runtime_cache.add(value)

def print_uniques(values: list[str] | None):
    if values is None:
        return
    unique_values = set(values) - runtime_cache
    for value in unique_values:
        print(value)
    runtime_cache.update(unique_values)

def read_stdin(verify_tty: bool = False):
    """
    Read values from standard input (stdin). 
    If `verify_tty` is True, exit if no input has been piped.
    """
    if verify_tty and sys.stdin.isatty():
        return
    try:
        for line in sys.stdin:
            yield line.strip()
    except KeyboardInterrupt:
        return

def process_stdin(
    *, 
    attr: str, 
    middleware: Callable[[str], schema.UrlObject], 
    callback: Callable[[str], None]
):
    for url in read_stdin():
        dissected: schema.UrlObject = middleware(url=url)
        if dissected: 
            callback(getattr(dissected, attr))

cli = Cli(
    description="Dissect and filter URLs provided on stdin.", 
    subcommand_metavar="[mode]", 
    subcommand_header="modes"
)

@cli.command('keys')
def keys_command():
    """Retrieve keys from the query string, one per line."""
    process_stdin(
        attr='keys', middleware=processor.urldissect, callback=print_uniques
    )


@cli.command('values')
def values_command():
    """Retrieve values from the query string, one per line."""
    process_stdin(
        attr='values', middleware=processor.urldissect, callback=print_uniques
    )


@cli.command('params')
def params_command():
    """Key=value pairs from the query string (one per line)"""
    process_stdin(
        attr='params', middleware=processor.urldissect, callback=print_uniques
    )


@cli.command('path')
def path_command():
    """Retrieve the path (e.g., /users/me)."""
    process_stdin(
        attr='path', middleware=processor.urldissect, callback=print_unique
    )


@cli.command('apex')
def apex_command():
    """Retrieve the apex domain (e.g., github.com)."""
    process_stdin(
        attr='apex', middleware=processor.urldissect, callback=print_unique
    )


@cli.command('fqdn')
def fqdn_command():
    """Retrieve the fully qualified domain name (e.g., api.github.com)."""
    process_stdin(
        attr='fqdn', middleware=processor.urldissect, callback=print_unique
    )


@cli.command('json')
def json_command():
    """JSON encode the dissected URL object."""
    process_stdin(
        attr='json', middleware=processor.urldissect, callback=print_unique
    )


@cli.command(name="filter", help="Refine URLs using component filters.")
@cli.option('-scheme', type=str, multiple=True, required=True, help="The request schemes (e.g. http, https)")
@cli.option('-sub', metavar='SUBDOMAIN', type=str, multiple=True, required=True, help="The subdomains (e.g. abc, abc.xyz)")
@cli.option('-domain', type=str, multiple=True, required=True, help="The domains (e.g. github, youtube)")
@cli.option('-tld', type=str, multiple=True, required=True, help="The top level domains (e.g. in, com)")
@cli.option('-ext', metavar='EXTENSION', type=str, multiple=True, required=True, help="The file extensions (e.g. pdf, html)")
@cli.option('-port', type=str, multiple=True, required=True, help="The ports (e.g. 22, 8080)")
@cli.option('-apex', type=str, multiple=True, required=True, help="The apex domains (e.g. github.com, youtube.com)")
@cli.option('-fqdn', type=str, multiple=True, required=True, help="The fully qualified domain names (e.g. api.github.com, app.example.com)")
@cli.option('-inverse', type=bool, help="Process filters as deny-list")
@cli.option('-strict', type=bool, help="Validate all filter checks")
@cli.option('-dissect', type=str, metavar="MODE", required=True, choices=[
    "keys", "values", "params", "path", "apex", "fqdn", "json"
], help="Dissect url and retrieve mode after filtering")
def filter_command(
    scheme: list[str] = None, 
    sub: list[str] = None,  
    domain: list[str] = None, 
    tld: list[str] = None, 
    ext: list[str] = None, 
    port: list[str] = None, 
    apex: list[str] = None, 
    fqdn: list[str] = None,
    inverse: bool = False,
    strict: bool = False,
    dissect: str = None
):
    """
    Refine URLs using component filters.
    By default, the command treats provided filters as an allow-list, 
    evaluating just one component of the url.

    To assess all components, add the `-strict` flag.
    For a deny-list approach, incorporate the `-inverse` flag.
    After evaluation, the default result is the URL.
    For specific URL dissected object, pair the `-dissect` option with any one of: 
    `keys` | `values` | `params` | `apex` | `fqdn` | `json`
    If `-dissect` is not provided, `filter` command aims to print 
    dissimilar urls using pattern matching
    """

    filters = schema.UrlFilters(
        schemes=scheme, subdomains=sub, domains=domain, tlds=tld, extensions=ext, 
        ports=port, apexes=apex, fqdns=fqdn, as_denylist=inverse
    )

    callback = print_unique
    middleware = partial(
        processor.urlfilter, filters=filters, strict=strict, return_obj=True
    )
    if dissect:
        if dissect in ('keys', 'values', 'params'):
            callback = print_uniques
        
        process_stdin(attr=dissect, middleware=middleware, callback=callback)
        return

    compiled = re.compile(r'(?<=/)\b\d+\b|(?<==)\b\d+\b')
    for url in read_stdin():
        url_object: schema.UrlObject = middleware(url=url)
        if url_object is None:
            continue

        separator = url.find(url_object.path or url_object.raw_query)
        if not separator:
            print_unique(url)
            continue
        
        clean_url = f"{url[0:separator]}{compiled.sub('0', url[separator:])}"
        if clean_url in runtime_cache:
            continue

        print(url)
        runtime_cache.add(clean_url)

if __name__ == "__main__":
    cli.run()