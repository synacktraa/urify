import argparse
from argparse import OPTIONAL, ZERO_OR_MORE, ONE_OR_MORE, PARSER, REMAINDER

class _ArgumentParser(argparse.ArgumentParser):

    class _ArgumentGroup(argparse._ArgumentGroup):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.title = self.title and self.title.title()

    class _HelpFormatter(argparse.RawDescriptionHelpFormatter):
        def _format_usage(self, *args, **kwargs) -> str:
            return super()._format_usage(*args, **kwargs).replace(
                'usage:', 'Usage:', 1
            )
        
        def _metavar_formatter(self, action, default_metavar):
            if None not in (action.metavar, action.choices):
                result = action.metavar
            else:
                result = default_metavar

            def format(tuple_size):
                if isinstance(result, tuple):
                    return result
                else:
                    return (result, ) * tuple_size
            return format

        def _include_subaction(self, action, parts: list):
            # if there are any sub-actions, add their help as well
            new_parts = parts.copy()
            for subaction in self._iter_indented_subactions(action):
                new_parts.append(self._format_action(subaction))

            # return a single string
            return self._join_parts(new_parts)
        
        def _format_args(self, action, default_metavar):
            get_metavar = self._metavar_formatter(action, default_metavar)
            if action.nargs is None:
                result = '%s' % get_metavar(1)
            elif action.nargs == argparse.OPTIONAL:
                result = '[%s]' % get_metavar(1)
            elif action.nargs == argparse.ZERO_OR_MORE:
                metavar = get_metavar(1)
                if len(metavar) == 2:
                    result = '[%s [%s ...]]' % metavar
                else:
                    result = '[%s ...]' % metavar
            elif action.nargs == argparse.ONE_OR_MORE:
                result = '%s [...]' % get_metavar(1)
            elif action.nargs == argparse.REMAINDER:
                result = '...'
            elif action.nargs == argparse.PARSER:
                result = '%s ...' % get_metavar(1)
            elif action.nargs == argparse.SUPPRESS:
                result = ''
            else:
                try:
                    formats = ['%s' for _ in range(action.nargs)]
                except TypeError:
                    raise ValueError("invalid nargs value") from None
                result = ' '.join(formats) % get_metavar(action.nargs)
            return result

        def _format_action(self, action):
            # determine the required width and the entry label
            help_position = min(self._action_max_length + 4,
                                self._max_help_position)
            help_width = max(self._width - help_position, 11)
            action_width = help_position - self._current_indent - 2 
            if type(action) is argparse._SubParsersAction:
                return self._include_subaction(action=action, parts=[''])

            action_header = self._format_action_invocation(action)

            # no help; start on same line and add a final newline
            if not action.help:
                tup = self._current_indent, '', action_header
                action_header = '%*s%s\n' % tup

            # short action name; start on the same line and pad two spaces
            elif len(action_header) <= action_width:
                tup = self._current_indent, '', action_width, action_header
                action_header = '%*s%-*s  ' % tup
                indent_first = 0

            # long action name; start on the next line
            else:
                tup = self._current_indent, '', action_header
                action_header = '%*s%s\n' % tup
                indent_first = help_position

            # collect the pieces of the action help
            parts = [action_header]

            # if there was help for the action, add lines of help text
            if action.help and action.help.strip():
                help_text = self._expand_help(action)
                if help_text:
                    help_lines = self._split_lines(help_text, help_width)
                    parts.append('%*s%s\n' % (indent_first, '', help_lines[0]))
                    for line in help_lines[1:]:
                        parts.append('%*s%s\n' % (help_position, '', line))

            # or add a newline if the description doesn't end with one
            elif not action_header.endswith('\n'):
                parts.append('\n')
            
            
            # Check if the action has choices and modify the formatting
            if action.choices is not None:
                choices_str = '|'.join(map(str, action.choices))
                parts += f"\n\n{action.metavar.title()}s:\n  {choices_str}\n"

            
            return self._include_subaction(action=action, parts=parts)

    def format_help(self):
        formatter = self._get_formatter()

        # description
        formatter.add_text(self.description)

        # usage
        formatter.add_usage(self.usage, self._actions,
                            self._mutually_exclusive_groups)

        # positionals, optionals and user-defined groups
        for action_group in self._action_groups:
            formatter.start_section(action_group.title)
            formatter.add_text(action_group.description)
            formatter.add_arguments(action_group._group_actions)
            formatter.end_section()

        # epilog
        formatter.add_text(self.epilog)

        # determine help from format above
        return formatter.format_help()

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs, formatter_class=self._HelpFormatter)

    def add_argument_group(self, *args, **kwargs) -> _ArgumentGroup:
        group = self._ArgumentGroup(self, *args, **kwargs)
        self._action_groups.append(group)
        return group