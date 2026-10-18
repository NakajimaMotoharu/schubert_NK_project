"""Explicit literal, finite, no-argument JUnit RepeatedTest declarations; no suffix stripping."""
import re


def expected(methods,declared,source):
    if len(methods)!=len(set(methods)):raise ValueError('unique normal invocation inventory')
    for name,count in declared.items():
        if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*',name) or type(count) is not int or not 1<=count<=100:
            raise ValueError('explicit finite integer repetition contract')
    matches=re.findall(r'@RepeatedTest\(\s*([1-9][0-9]*)\s*\)\s+void\s+([A-Za-z][A-Za-z0-9_]*)\(\s*\)',source)
    actual={name:int(count) for count,name in matches}
    if source.count('@RepeatedTest')!=len(matches) or len(actual)!=len(matches) or actual!=declared:
        raise ValueError('all literal RepeatedTest declarations must exactly match the allowlist')
    if '@ParameterizedTest' in source or '@TestTemplate' in source:
        raise ValueError('unsupported invocation generator requires separate explicit qualification')
    if set(methods)&set(declared):raise ValueError('repeated method cannot also be a normal test')
    expanded=list(methods)
    for name,count in declared.items():
        expanded.extend(f'{name}()[{number}]' for number in range(1,count+1))
    if len(expanded)!=len(set(expanded)):raise ValueError('repetition/normal/alias invocation collision')
    return sorted(expanded)


def detail(invocation,declared):
    for name,count in declared.items():
        match=re.fullmatch(re.escape(name)+r'\(\)\[([1-9][0-9]*)\]',invocation)
        if match:
            number=int(match[1])
            if number>count:raise ValueError('repetition number exceeds its literal declaration')
            return {'declaredMethod':name,'observedInvocation':invocation,
                    'declaredRepetition':{'number':number,'count':count}}
    return {}
