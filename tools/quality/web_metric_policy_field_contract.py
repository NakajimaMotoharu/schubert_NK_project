"""Fixed javap declaration/descriptor pairs for the public stateless Web scrape policy."""
import re

PREFIX = 'dev.codex.schubert.nk.web.monitoring.'
METHODS = {
    '  public ' + PREFIX + 'WebMetricScrape();': '    descriptor: ()V',
    '  public java.lang.String scrape(io.micrometer.core.instrument.MeterRegistry, java.lang.String);': '    descriptor: (Lio/micrometer/core/instrument/MeterRegistry;Ljava/lang/String;)Ljava/lang/String;'}


def require(value, message):
    if not value:
        raise ValueError(message)


def verify_contract(text, expected):
    lines = [line for line in text.splitlines() if line.strip()]
    require(lines[:2] == ['Compiled from "WebMetricScrape.java"', 'public final class ' + PREFIX + 'WebMetricScrape {'] and lines[-1] == '}', 'exact known policy class grammar')
    body = lines[2:-1]
    require(len(body) % 2 == 0, 'each declaration has exactly one descriptor')
    fields, methods = {}, {}
    for index in range(0, len(body), 2):
        declaration, descriptor = body[index:index + 2]
        field = re.fullmatch(r'  private final ([A-Za-z0-9_.$]+) ([A-Za-z0-9_]+);', declaration)
        if field is not None:
            type_name, name = field.groups()
            require(name not in fields and descriptor == '    descriptor: L' + type_name.replace('.', '/') + ';', 'unique field and exact physical descriptor')
            fields[name] = type_name
        else:
            require(declaration in METHODS and declaration not in methods and descriptor == METHODS[declaration], 'only exact two public methods, not descriptor-as-field')
            methods[declaration] = descriptor
    require(fields == expected and methods == METHODS, 'all exact formatter fields and public API, no retained source or extra method')
    return fields, methods


def negative_guards(text, expected):
    first_name = next(iter(expected))
    first_type = expected[first_name]
    pair = '  private final ' + first_type + ' ' + first_name + ';\n    descriptor: L' + first_type.replace('.', '/') + ';\n'
    require(text.count(pair) == 1, 'independent first field fixture present')
    extra_field = '  private final io.micrometer.core.instrument.MeterRegistry source;\n    descriptor: Lio/micrometer/core/instrument/MeterRegistry;\n'
    extra_method = '  public java.lang.String extra();\n    descriptor: ()Ljava/lang/String;\n'
    cases = (
        ('retained-source', text.replace(pair, pair + extra_field, 1)),
        ('public-field', text.replace('  private final ', '  public final ', 1)),
        ('wrong-descriptor', text.replace('    descriptor: L' + first_type.replace('.', '/') + ';', '    descriptor: Ljava/lang/String;', 1)),
        ('extra-method', text.replace('\n}', '\n' + extra_method + '}', 1)),
        ('missing-field', text.replace(pair, '', 1)))
    rejected = []
    for name, mutant in cases:
        try:
            verify_contract(mutant, expected)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('every declaration/descriptor negative must reject')
    return rejected
