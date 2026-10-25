"""Bounded ordinary Java String literal metadata, no parsing/execution of Java programs."""
import json
from public_java_digest_provenance import LEX


def string_value(token):
    if not token.startswith('"') or not token.endswith('"') or token.startswith('"""') or len(token) < 2:
        raise ValueError('ordinary closed String literal only')
    body = token[1:-1]
    out = []
    index = 0
    escapes = {'b':'\b','t':'\t','n':'\n','f':'\f','r':'\r','"':'"',"'":"'",'\\':'\\','s':' '}
    while index < len(body):
        ch = body[index]
        if ch in '\n\r"':
            raise ValueError('unescaped control/quote is not ordinary String metadata')
        if ch != '\\':
            out.append(ch)
            index += 1
            continue
        index += 1
        if index == len(body):
            raise ValueError('incomplete escape')
        ch = body[index]
        if ch in escapes:
            out.append(escapes[ch])
            index += 1
        elif ch in '01234567':
            limit = 3 if ch in '0123' else 2
            end = index+1
            while end < min(len(body),index+limit) and body[end] in '01234567':
                end += 1
            out.append(chr(int(body[index:end],8)))
            index = end
        else:
            raise ValueError('unknown escape or unsupported Unicode preprocessing')
    return ''.join(out)


def core_tokens(text):
    tokens = [m.group() for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]
    out = []
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token.startswith('"'):
            value = string_value(token)
            index += 1
            while index+1 < len(tokens) and tokens[index] == '+' and tokens[index+1].startswith('"'):
                value += string_value(tokens[index+1])
                index += 2
            out.append(json.dumps(value,ensure_ascii=False))
        else:
            out.append(token)
            index += 1
    return ''.join(out)


def vectors():
    for source, expected in (
        ('"a" + "b"','ab'),
        ('"select " + "x" + " from y"','select x from y'),
        ('"a\\\\" + "b"','a\\b'),
        ('"\\\"" + "é"','"é'),
        ('"\\1" + "23"','\x0123'),
        ('"\\377" + "7"','ÿ7')):
        assert core_tokens(source) == json.dumps(expected,ensure_ascii=False)
    for invalid in ('"unfinished','"\\q"','"\\u0041"','"""text"""'):
        try:
            string_value(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError('unsupported or invalid literal accepted')
    return 10
