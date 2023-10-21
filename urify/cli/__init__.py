import sys
from pydantic import BaseModel
from typing import Callable, Any, Type

from .base import _ArgumentParser, OPTIONAL, ZERO_OR_MORE, ONE_OR_MORE


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
    

class Command(BaseModel):
    """
    Represents a command-line command.

    :param name `(str)`: The name of the command.
    :param callback `(Callable[..., Any])`: The function to be called when the command is invoked.
    :param parser `(_ArgumentParser)`: The argument parser associated with this command.
    """
    name: str
    callback: Callable[..., Any]
    parser: _ArgumentParser

    class Config:
        arbitrary_types_allowed = True


class Cli:
    """
    A command-line interface (CLI) parser, providing an improved interface over `argparse.ArgumentParser`.

    The `Cli` class aims to offer a more intuitive and concise way to define command-line interfaces, 
    drawing inspiration from popular libraries like `click` and `typer`, while retaining some unique features of `argparse`.

    :param description `(str, optional)`: A brief description of the command-line tool. Displayed when help is requested.
    :param epilog `(str, optional)`: Additional information displayed at the end of the help message.
    :param help_flag `(str, optional)`: Custom flag for displaying help. Defaults to '-help'.
    :param subcommand_header `(str, optional)`: Header for the subcommands section in the help message. Defaults to "commands".
    :param subcommand_metavar `(str, optional)`: Placeholder for subcommands in the help message. Defaults to "[command]".
    """

    def __init__(
        self, 
        description: str = None, 
        epilog: str = None, 
        help_flag: str = '-help',
        subcommand_header: str = "commands",
        subcommand_metavar: str = "[command]",
    ) -> None:
        """Initializes the CLI parser."""
        
        self._parser = _ArgumentParser(
            description=description, epilog=epilog, add_help=False
        ) 
        self._help_flag = help_flag
        self._help_ctx = {'action': 'help', 'help': 'show this help message'}
        self._add_help(self._parser)
        self._subcommand_parser = self._parser.add_subparsers(
            dest="subcommand", title=subcommand_header, metavar=subcommand_metavar
        )
        self._registered_commands: dict[str, Command] = {}
        self._pending_options = []

    def _add_help(self, parser: _ArgumentParser):
        """Internal method to add a help option to the parser."""
        parser.add_argument(self._help_flag, **self._help_ctx)

    def command(
        self, name: str=None, *, help: str=None, epilog: str=None
    ):
        """
        Decorator to register a function as a command.

        :param name `(str, optional)`: Custom name for the command. Defaults to the function's name.
        :param help `(str, optional)`: Brief description of the command. If not provided, it defaults to the function's docstring.
        :param epilog `(str, optional)`: Additional information displayed at the end of the command's help message.
        """

        def decorator(func: Callable[..., Any]):
            doc = '\n'.join(
                line.strip() for line in func.__doc__.split('\n')
            )
            _name = name or func.__name__
            _parser = self._subcommand_parser.add_parser(
                _name, help=help or doc, description=doc or help, epilog=epilog, add_help=False
            )
            self._add_help(_parser)
            command = Command(name=_name, callback=func, parser=_parser)
            
            # Add all the pending options to this command
            for option_args, option_kwargs in self._pending_options:
                _parser.add_argument(*option_args, **option_kwargs)
            
            # Clear the pending options
            self._pending_options.clear()

            # Register the command
            self._registered_commands[_name] = command
            return func
        
        return decorator
    
    def option(
        self, 
        flag: str, 
        *, 
        help: str=None, 
        type: Type, 
        choices: list[str] = None,
        multiple: bool = False, 
        metavar: str = None, 
        required: bool = False,
    ):
        """
        Decorator to register an argument for a command.

        :param flag `(str)`: The flag used to specify the argument in the command line.
        :param help `(str, optional)`: Description of what the argument does.
        :param type `(Type)`: Expected data type of the argument's value.
        :param choices `(list[str], optional)`: A list of valid values for the argument.
        :param multiple `(bool, optional)`: If set to True, allows multiple values for the argument.
        :param metavar `(str, optional)`: Placeholder for the argument in the help message.
        :param required `(bool, optional)`: If set to True, the argument is mandatory.
        """

        if type is bool:
            kwargs = {
                'action': 'store_true', 'required': required
            }
        else:
            kwargs = {
                'type': type, 'metavar': metavar, 'choices': choices
            }
            if multiple and required:
                kwargs.update({'nargs': ONE_OR_MORE})
            elif multiple and not required:
                kwargs.update({'nargs': ZERO_OR_MORE})
            elif not multiple and required:
                kwargs.update({'nargs': None})
            else:
                kwargs.update({'nargs': OPTIONAL})
        
        def decorator(func: Callable[..., Any]):
            self._pending_options.insert(
                0, ([flag], {'help': help,  **kwargs})
            )
            return func
        
        return decorator
    
    def run(self):
        """Parses the command line arguments and invokes the appropriate command."""
        parsed = self._parser.parse_args()
        invoked = parsed.__dict__.pop('subcommand')
        if invoked is None:
            self._parser.print_help()
            return
        command = self._registered_commands[invoked]
        command.callback(**parsed.__dict__)
        