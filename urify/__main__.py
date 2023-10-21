from .cli import Cli, read_stdin
from .core import schema, processor


cli = Cli(
    description="Dissect and filter URLs provided on stdin.", 
    subcommand_metavar="[mode]", 
    subcommand_header="modes"
)

@cli.command('keys')
def keys_command():
    """Retrieve keys from the query string, one per line."""
    for url in read_stdin():
        dissected = processor.urldissect(url=url)
        if dissected and dissected.keys:
            print('\n'.join(dissected.keys))


@cli.command('values')
def values_command():
    """Retrieve values from the query string, one per line."""
    for url in read_stdin():
        dissected = processor.urldissect(url=url)
        if dissected and dissected.values:
            print('\n'.join(dissected.values))


@cli.command('params')
def params_command():
    """Key=value pairs from the query string (one per line)"""
    for url in read_stdin():
        dissected = processor.urldissect(url=url)
        if dissected and dissected.params:
            print('\n'.join(dissected.params))


@cli.command('path')
def path_command():
    """Retrieve the path (e.g., /users/me)."""
    for url in read_stdin():
        dissected = processor.urldissect(url=url)
        if dissected and dissected.path:
            print(dissected.path)


@cli.command('apex')
def apex_command():
    """Retrieve the apex domain (e.g., github.com)."""
    for url in read_stdin():
        dissected = processor.urldissect(url=url)
        if dissected and dissected.apex:
            print(dissected.apex)


@cli.command('fqdn')
def fqdn_command():
    """Retrieve the fully qualified domain name (e.g., api.github.com)."""
    for url in read_stdin():
        dissected = processor.urldissect(url=url)
        if dissected and dissected.fqdn:
            print(dissected.fqdn)


@cli.command('json')
def json_command():
    """JSON encode the dissected URL object."""
    for url in read_stdin():
        dissected = processor.urldissect(url=url)
        if dissected:print(dissected.json())


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
@cli.option('-absolute', type=bool, help="Validate all filter checks")
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
    absolute: bool = False,
    dissect: str = None
):
    """
    Refine URLs using component filters.
    By default, the command treats provided filters as an allow-list, 
    evaluating just one parameter from a specified field.

    To assess all components, add the `-absolute` flag.
    For a deny-list approach, incorporate the `-inverse` flag.
    After evaluation, the default result is the URL.
    For specific URL dissected object, pair the `-dissect` option with any one of: 
    `keys` | `values` | `params` | `apex` | `fqdn` | `json`
    """

    filters = schema.UrlFilters(
        schemes=scheme, subdomains=sub, domains=domain, tlds=tld, extensions=ext, 
        ports=port, apexes=apex, fqdns=fqdn, as_denylist=inverse
    )
    for url in read_stdin():
        dissected = processor.urlfilter(
            url=url, filters=filters, absolute=absolute, return_obj=True
        )
        if not dissected:continue
        if dissect:
        
            value = getattr(dissected, dissect)
            if callable(value): value = value()
            if type(value) is list: 
                print('\n'.join(value))
            else: print(value)
        else: print(url)
    

if __name__ == "__main__":
    cli.run()