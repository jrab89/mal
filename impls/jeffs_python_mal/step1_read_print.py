import readline  # noqa: F401
from dataclasses import dataclass
# from enum import Enum, auto


@dataclass
class LeftParen:
    pass


@dataclass
class RightParen:
    pass


@dataclass
class Symbol:
    name: str

# @dataclass
# class Number:
#     value: str


Token = LeftParen | RightParen | Symbol | int | str


# class MultiCharToken(Enum):
#     symbol = auto()
#     integer = auto()
#     string = auto()


# def READ(source: str) -> list[Token]:
#     """
#     Given a source code string, return tokens

#     >>> READ("()")
#     [LeftParen(), RightParen()]

#     >>> READ('( "foo")')
#     [LeftParen(), 'foo', RightParen()]

#     >>> READ('( () 3 "foo" 1)')
#     [LeftParen(), LeftParen(), RightParen(), 3, 'foo', 1, RightParen()]

#     >>> READ('( () 3 "foo" 999)')
#     [LeftParen(), LeftParen(), RightParen(), 3, 'foo', 999, RightParen()]
#     """
#     tokens: list[Token] = []
#     inside_token: MultiCharToken | None = None
#     multi_char_token_text = ""

#     for index, char in enumerate(source):
#         if not inside_token:
#             if char == "(":
#                 tokens.append(LeftParen())
#             elif char == ")":
#                 tokens.append(RightParen())
#             elif char == '"':
#                 inside_token = MultiCharToken.string
#             elif char in "0123456789":
#                 if source[index + 1] not in "0123456789":
#                     tokens.append(int(char))
#                 else:
#                     inside_token = MultiCharToken.integer
#                     multi_char_token_text += char
#         elif inside_token is MultiCharToken.string:
#             if char == '"':
#                 tokens.append(multi_char_token_text)
#                 multi_char_token_text = ""
#                 inside_token = None
#             else:
#                 multi_char_token_text += char
#         elif inside_token is MultiCharToken.integer:
#             multi_char_token_text += char
#             if source[index + 1] not in "0123456789":
#                 tokens.append(int(multi_char_token_text))
#                 multi_char_token_text = ""
#                 inside_token = None

#     return tokens


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


def recursive_READ(source: str) -> list[Token]:
    """
    Given a source code string, return tokens

    >>> recursive_READ("()")
    [LeftParen(), RightParen()]

    >>> recursive_READ('( "foo")')
    [LeftParen(), 'foo', RightParen()]

    >>> recursive_READ('( () 3 "foo" 12) 66')
    [LeftParen(), LeftParen(), RightParen(), 3, 'foo', 12, RightParen(), 66]

    >>> recursive_READ('abc')
    [Symbol(name='abc')]

    >>> recursive_READ('(->>) 3 "foo" 12 66')
    [LeftParen(), Symbol(name='->>'), RightParen(), 3, 'foo', 12, 66]
    """
    if source == "":
        return []
    elif source[0] == "(":
        return [LeftParen()] + recursive_READ(source[1:])
    elif source[0] == ")":
        return [RightParen()] + recursive_READ(source[1:])
    elif source[0] == '"':
        string_token, leftover_source = read_str(source[1:])
        return [string_token] + recursive_READ(leftover_source)
    elif source[0] in "0123456789":
        int_token, leftover_source = read_int(source)
        return [int_token] + recursive_READ(leftover_source)
    elif source[0] not in " \n\t,;()":
        symbol_token, leftover_source = read_symbol(source)
        return [symbol_token] + recursive_READ(leftover_source)
    else:
        return recursive_READ(source[1:])


def READ(source: str) -> list[Token]:
    return []


def EVAL(tokens: list[Token]) -> list[Token]:
    return tokens


def PRINT(tokens: list[Token]) -> str:
    return "TODO"


if __name__ == "__main__":
    while True:
        try:
            source = input("user> ")
            tokens = READ(source)
            PRINT(EVAL(tokens))
        except EOFError:
            break
