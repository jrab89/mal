import readline  # noqa: F401
from dataclasses import dataclass
from typing import Iterable
import string


@dataclass(frozen=True)
class LeftParen():
    def __str__(self) -> str:
        return "("


@dataclass(frozen=True)
class RightParen:
    def __str__(self) -> str:
        return ")"


@dataclass(frozen=True)
class Symbol:
    name: str

    def __str__(self) -> str:
        return self.name


Token = LeftParen | RightParen | Symbol | str | int

_INT_CHARS = set(string.digits)
_PRINTABLE_ASCII_CHARS = set(string.printable)
_WHITESPACE_CHARS = set(string.whitespace + ",")
_SYMBOL_CHARS = _PRINTABLE_ASCII_CHARS - _WHITESPACE_CHARS
_PARENS = {"(", ")"}


def _scan_symbol(source: str, symbol_start_index: int) -> tuple[Symbol, int]:
    """
    Given a source code string and the index of the first character of a
    symbol, return the symbol token and the new index to continue lexing
    at (the index of the first character after the symbol token)

    >>> _scan_symbol('foo bar baz', 4)
    (Symbol(name='bar'), 7)
    >>> _scan_symbol('x', 0)
    (Symbol(name='x'), 1)
    """
    for index, char in enumerate(source[symbol_start_index:]):
        if char in _WHITESPACE_CHARS:
            symbol_name = source[symbol_start_index:index + symbol_start_index]
            return (Symbol(symbol_name),
                    index + symbol_start_index)

    symbol_name = source[symbol_start_index:len(source)]
    return (Symbol(symbol_name), len(source))


def _scan_int(source: str, int_start_index: int) -> tuple[int, int]:
    """
    Given a source code string and the index of the first digit on an int,
    return the int token and the new index to continue lexing at (the index of
    the first character after the int token)

    >>> _scan_int('foo 123 baz', 4)
    (123, 7)
    >>> _scan_int('0', 0)
    (0, 1)
    >>> _scan_int('5)', 0)
    (5, 1)
    >>> _scan_int('0invalid', 0)
    Traceback (most recent call last):
     ...
    ValueError: invalid literal for int() with base 10: '0invalid'
    """
    for index, char in enumerate(source[int_start_index:]):
        if char in _WHITESPACE_CHARS | _PARENS:
            return (int(source[int_start_index:index + int_start_index]),
                    index + int_start_index)

    return (int(source[int_start_index:len(source)]), len(source))


def _scan_str(source: str, str_start_index: int) -> tuple[str, int]:
    """
    Given a source code string and the index of a double-quote that starts
    a string token, return the string token and the new index to continue
    lexing at (the index of the first character after the string token's
    double quote)

    >>> _scan_str('foo "bar" baz', 4)
    ('bar', 9)
    >>> _scan_str('"bar"', 0)
    ('bar', 5)
    >>> _scan_str('foo "bar baz', 4)
    Traceback (most recent call last):
     ...
    Exception: unbalanced quotes starting at 4
    """
    current_char_index = str_start_index + 1
    while current_char_index < len(source):
        if source[current_char_index] == '"':
            return (source[str_start_index + 1:current_char_index],
                    current_char_index + 1)
        current_char_index += 1

    raise Exception(f"unbalanced quotes starting at {str_start_index}")


def lex(source: str) -> Iterable[Token]:
    """
    Given a source code string, return tokens

    >>> list(lex("()"))
    [LeftParen(), RightParen()]
    >>> list(lex('( "foo")'))
    [LeftParen(), 'foo', RightParen()]
    >>> list(lex('( () 3 "foo" 12'))
    [LeftParen(), LeftParen(), RightParen(), 3, 'foo', 12]
    >>> list(lex('abc "foo" +'))
    [Symbol(name='abc'), 'foo', Symbol(name='+')]
    >>> list(lex('(->>) 3 "foo" 12 66'))
    [LeftParen(), Symbol(name='->>)'), 3, 'foo', 12, 66]
    >>> list(lex("💣"))
    Traceback (most recent call last):
     ...
    Exception: Non-printable-ASCII character at 0
    """
    current_char_index = 0
    while current_char_index < len(source):
        if source[current_char_index] not in _PRINTABLE_ASCII_CHARS:
            raise Exception(
                f"Non-printable-ASCII character at {current_char_index}"
            )
        if source[current_char_index] == "(":
            current_char_index += 1
            yield LeftParen()
        elif source[current_char_index] == ")":
            current_char_index += 1
            yield RightParen()
        elif source[current_char_index] == '"':
            string_token, new_char_index = _scan_str(source,
                                                     current_char_index)
            current_char_index = new_char_index
            yield string_token
        elif source[current_char_index] in _INT_CHARS:
            int_token, new_char_index = _scan_int(source,
                                                  current_char_index)
            current_char_index = new_char_index
            yield int_token
        elif source[current_char_index] in _SYMBOL_CHARS:
            symbol_token, new_char_index = _scan_symbol(source,
                                                        current_char_index)
            current_char_index = new_char_index
            yield symbol_token
        elif source[current_char_index] == '"':
            str_token, new_char_index = _scan_str(source,
                                                  current_char_index)
            current_char_index = new_char_index
            yield str_token
        else:
            current_char_index += 1


def READ(source: str) -> Iterable[Token]:
    return lex(source)


def EVAL(tokens: Iterable[Token]) -> Iterable[Token]:
    return tokens


def _preceed_with_space(previous: Token | None, current: Token) -> bool:
    if not previous:
        return False

    # `None` here means a non-paren token
    previous_token_type = (
        previous if isinstance(previous, LeftParen | RightParen)
        else None
    )
    current_token_type = (
        current if isinstance(current, LeftParen | RightParen)
        else None
    )

    rules: dict[tuple[LeftParen | RightParen | None, LeftParen | RightParen | None], bool] = {
        (None, LeftParen()): True,            # "something ("
        (None, RightParen()): False,          # "something)"
        (None, None): True,                   # "something something"
        (LeftParen(), LeftParen()): False,    # "(("
        (LeftParen(), RightParen()): False,   # "()"
        (LeftParen(), None): False,           # "(something"
        (RightParen(), LeftParen()): True,    # ") ("
        (RightParen(), RightParen()): False,  # "))"
        (RightParen(), None): True,           # ") something"
    }

    return rules[(previous_token_type, current_token_type)]


def PRINT(tokens: Iterable[Token]) -> str:
    """
    Given tokens, return a nicely formatted str of them
    >>> PRINT([LeftParen(), RightParen()])
    '()'
    >>> PRINT([1])
    '1'
    >>> PRINT([LeftParen(), Symbol(name='+'), 1, 2, RightParen()])
    '(+ 1 2)'
    >>> PRINT(READ('(+ 1 (+ 2 3))'))
    '(+ 1 (+ 2 3))'
    >>> PRINT(READ('(()())'))
    '(() ())'
    >>> PRINT(READ('"abc"'))
    '"abc"'
    """
    strs: list[str] = []
    previous: Token | None = None
    for current in tokens:
        current_str = f'"{current}"' if isinstance(current, str) else str(current)
        if _preceed_with_space(previous, current):
            strs.append(" ")
        strs.append(current_str)
        previous = current

    return "".join(strs)


if __name__ == "__main__":
    while True:
        try:
            source = input("user> ")
            tokens = READ(source)
            print(PRINT(EVAL(tokens)))
        except EOFError:
            break
        except Exception as e:
            print(e)
