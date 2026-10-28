"""Strict positional diagnostic matching, including comma-grouped lines and one known message pair."""
import re

LOADER = 'In J2EE, getClassLoader() might not work as expected. Use Thread.currentThread().getContextClassLoader() instead.'

def signature(attributes,message):
    attrs = tuple(sorted((k,v) for k,v in attributes.items() if k not in ['beginline','endline','begincolumn','endcolumn']))
    if attributes['rule'] == 'AvoidDuplicateLiterals':
        match = re.fullmatch(r'(The String literal ".*" appears \d+ times in this file; the first occurrence is on line )([0-9]+|[0-9]{1,3}(?:,[0-9]{3})+)',message)
        assert match and int(match[2].replace(',','')) == int(attributes['beginline'])
        message = match[1]+'<POSITION>'
    elif attributes['rule'] == 'UseProperClassLoader':
        assert message in [LOADER,LOADER.replace('expected. Use','expected.  Use')]
        message = LOADER
    return attrs,message

def selftest():
    attrs = dict(rule='AvoidDuplicateLiterals',beginline='1009',endline='1009',method='x',**{'class':'T'})
    original = 'The String literal "fixture" appears 4 times in this file; the first occurrence is on line 1,009'
    after_attrs = dict(attrs,beginline='1145',endline='1145')
    after = original.replace('1,009','1,145');assert signature(attrs,original) == signature(after_attrs,after)
    assert signature(attrs,original.replace('1,009','1009')) == signature(attrs,original)
    loader = dict(attrs,rule='UseProperClassLoader');assert signature(loader,LOADER) == signature(loader,LOADER.replace('expected. Use','expected.  Use'))
    cases = [('literal',after_attrs,after.replace('fixture','wrong')),('count',after_attrs,after.replace('4 times','5 times')),
        ('class',dict(after_attrs,**{'class':'Other'}),after),('method',dict(after_attrs,method='other'),after),
        ('grammar',after_attrs,after.replace('1,145','1,14')),('anchor',dict(after_attrs,beginline='1144'),after),
        ('loader',loader,LOADER.replace('J2EE','unknown'))]
    rejected = []
    for label,a,m in cases:
        reference = signature(attrs,original) if label != 'loader' else signature(loader,LOADER)
        try:result = signature(a,m)
        except (AssertionError,ValueError):rejected.append(label);continue
        assert result != reference;rejected.append(label)
    return dict(positive=3,negative=len(rejected),labels=rejected)
