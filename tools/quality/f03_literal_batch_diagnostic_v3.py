"""Match the original global finding schema, while source token inverses protect raw literal values."""
import re

def signature(attributes,message):
    # PG10690 originally exported itertext with split/join. This is diagnostic schema,
    # never a normalization of source values or executable/oracle tokens.
    message = ' '.join(message.split())
    attrs = tuple(sorted((k,v) for k,v in attributes.items() if k not in ['beginline','endline','begincolumn','endcolumn']))
    if attributes['rule'] == 'AvoidDuplicateLiterals':
        match = re.fullmatch(r'(The String literal ".*" appears \d+ times in this file; the first occurrence is on line )([0-9]+|[0-9]{1,3}(?:,[0-9]{3})+)',message)
        assert match and int(match[2].replace(',','')) == int(attributes['beginline'])
        message = match[1]+'<POSITION>'
    return attrs,message

def selftest():
    a = dict(rule='AvoidDuplicateLiterals',beginline='1009',method='x',**{'class':'T'})
    first = 'The String literal "fixture" appears 4 times in this file; the first occurrence is on line 1,009'
    b = dict(a,beginline='1145');second = first.replace('1,009','1145')
    assert signature(a,first) == signature(b,second)
    assert signature(dict(a,rule='Other'),'fixed  diagnostic\nmessage') == signature(dict(a,rule='Other'),'fixed diagnostic message')
    cases = [('literal',b,second.replace('fixture','wrong')),('count',b,second.replace('4 times','5 times')),
        ('class',dict(b,**{'class':'Other'}),second),('method',dict(b,method='other'),second),
        ('grammar',b,second.replace('1145','1,14')),('anchor',dict(b,beginline='1144'),second)]
    rejected = []
    for label,attrs,text in cases:
        try:value = signature(attrs,text)
        except (AssertionError,ValueError):rejected.append(label);continue
        assert value != signature(a,first);rejected.append(label)
    return dict(positive=2,negative=len(rejected),labels=rejected,rawLiteralWhitespaceProtectedBySeparateWholeSourceTokenInverse=True)
