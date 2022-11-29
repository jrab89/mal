import readline  # noqa: F401
from dataclasses import dataclass


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


@dataclass(frozen=True)
class StringToken:
    value: str

    def __str__(self) -> str:
        return f'"{self.value}"'


Token = LeftParen | RightParen | Symbol | StringToken | int


def read_str(source: str) -> tuple[StringToken, str]:
    result = ""
    for index, char in enumerate(source):
        if char == '"':
            return (StringToken(result), source[index + 1:])
        result += char
    raise EOFError("unbalanced quotes")


def read_int(source: str) -> tuple[int, str]:
    result = ""
    for index, char in enumerate(source):
        if char not in "0123456789":
            return (int(result), source[index:])
        result += char
    return (int(result), "")


def read_symbol(source: str) -> tuple[Symbol, str]:
    result = ""
    for index, char in enumerate(source):
        if char in " \n\t,;()":
            return (Symbol(result), source[index:])
        result += char
    return (Symbol(result), "")


def READ(source: str) -> list[Token]:
    """
    Given a source code string, return tokens

    >>> READ("()")
    [LeftParen(), RightParen()]

    >>> READ('( "foo")')
    [LeftParen(), StringToken(value='foo'), RightParen()]

    >>> READ('( () 3 "foo" 12')
    [LeftParen(), LeftParen(), RightParen(), 3, StringToken(value='foo'), 12]

    >>> READ('abc "foo" +')
    [Symbol(name='abc'), StringToken(value='foo'), Symbol(name='+')]

    >>> READ('(->>) 3 "foo" 12 66')
    [LeftParen(), Symbol(name='->>'), RightParen(), 3, 12, 66]
    """
    if source == "":
        return []
    elif source[0] == "(":
        return [LeftParen()] + READ(source[1:])
    elif source[0] == ")":
        return [RightParen()] + READ(source[1:])
    elif source[0] == '"':
        string_token, leftover_source = read_str(source[1:])
        return [string_token] + READ(leftover_source)
    elif source[0] in "0123456789":
        int_token, leftover_source = read_int(source)
        return [int_token] + READ(leftover_source)
    elif source[0] not in " \n\t,;()":
        symbol_token, leftover_source = read_symbol(source)
        return [symbol_token] + READ(leftover_source)
    else:
        return READ(source[1:])


def EVAL(tokens: list[Token]) -> list[Token]:
    return tokens


def PRINT(tokens: list[Token]) -> str:
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
    """

    strs: list[str] = []
    for index, current in enumerate(tokens):
        previous = tokens[index - 1] if index > 0 else None

        if preceed_with_space(previous, current):
            strs.append(f" {current}")
        else:
            strs.append(str(current))

    return "".join(strs)


def preceed_with_space(previous: Token | None, current: Token) -> bool:
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


if __name__ == "__main__":
    while True:
        try:
            source = input("user> ")
            tokens = READ(source)
            print(PRINT(EVAL(tokens)))
        except EOFError:
            break
