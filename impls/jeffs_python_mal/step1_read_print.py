import readline  # noqa: F401
from dataclasses import dataclass


@dataclass
class LeftParen:
    def __str__(self) -> str:
        return "("


@dataclass
class RightParen:
    def __str__(self) -> str:
        return ")"


@dataclass
class Symbol:
    name: str

    def __str__(self) -> str:
        return self.name


Token = LeftParen | RightParen | Symbol | int | str


def read_str(source: str) -> tuple[str, str]:
    result = ""
    for index, char in enumerate(source):
        if char == '"':
            return (result, source[index + 1:])
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
    [LeftParen(), 'foo', RightParen()]

    >>> READ('( () 3 "foo" 12) 66')
    [LeftParen(), LeftParen(), RightParen(), 3, 'foo', 12, RightParen(), 66]

    >>> READ('abc "foo" +')
    [Symbol(name='abc'), 'foo', Symbol(name='+')]

    >>> READ('(->>) 3 "foo" 12 66')
    [LeftParen(), Symbol(name='->>'), RightParen(), 3, 'foo', 12, 66]
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
        upcoming = tokens[index + 1] if index + 1 < len(tokens) else None

        previous_paren = type(previous) in [LeftParen, RightParen]
        current_paren = type(current) in [LeftParen, RightParen]
        upcoming_paren = type(upcoming) in [LeftParen, RightParen]

        if not previous:
            strs.append(str(current))
        elif current_paren:
            if previous_paren:
                if current == previous or not upcoming:
                    strs.append(str(current))
                else:
                    strs.append(f" {current}")
            else:
                if upcoming_paren or not upcoming:
                    strs.append(str(current))
                else:
                    strs.append(f" {current}")
        else:
            if previous_paren:
                strs.append(str(current))
            else:
                strs.append(f" {current}")

    return "".join(strs)


if __name__ == "__main__":
    while True:
        try:
            source = input("user> ")
            tokens = READ(source)
            print(PRINT(EVAL(tokens)))
        except EOFError:
            break
