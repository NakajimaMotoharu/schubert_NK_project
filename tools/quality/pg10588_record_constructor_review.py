"""Freeze constructor body review; value preservation is not whole oracle/PT qualification."""
from collections import Counter
from pathlib import Path
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10518_constructor_carrier_review import lex

OUT = data.BASE/'PG10588-record-constructor-review-v1'


def closing(values,begin,left,right):
    depth = 1
    for i in range(begin+1,len(values)):
        if values[i][0] == left:
            depth += 1
        elif values[i][0] == right:
            depth -= 1
        if depth == 0:
            return i
    raise ValueError('complete source scope required')


def parameters(values):
    parts,current = [],[]
    angle,parenthesis,bracket = 0,0,0
    for value,_,_ in values:
        if value == ',' and angle == parenthesis == bracket == 0:
            parts.append(current)
            current = []
            continue
        current.append(value)
        if value == '<': angle += 1
        elif value == '>': angle -= 1
        elif value == '(': parenthesis += 1
        elif value == ')': parenthesis -= 1
        elif value == '[': bracket += 1
        elif value == ']': bracket -= 1
    if current: parts.append(current)
    assert angle == parenthesis == bracket == 0
    names = []
    for part in parts:
        identifiers = [value for value in part if re.fullmatch('[A-Za-z_$][A-Za-z0-9_$]*',value)]
        assert identifiers
        names.append(identifiers[-1])
    assert len(names) == len(set(names))
    return names


def body_contract(body,names):
    values = [value for value,_,_ in lex(body)]
    assignments = []
    for i,value in enumerate(values[:-2]):
        if value not in names:
            continue
        if values[i+1] == '=' and values[i+2] != '=':
            end = values.index(';',i+2)
            rhs = values[i+2:end]
            if rhs != ['List','.','copyOf','(',value,')']:
                raise ValueError('component computation/normalization requires separate review')
            assignments.append(dict(component=value,kind='JDK_LIST_COPY_SAME_ELEMENTS_AND_ORDER'))
        elif values[i+1:i+3] in (['+','+'],['-','-']) or (values[i+1] in ('+','-','*','/') and values[i+2] == '='):
            raise ValueError('component mutation is not a validation-only constructor')
        elif values[i+1] == '.' and values[i+2] in {'add','remove','clear','set','put','sort','replaceAll','poll','pop','push'}:
            raise ValueError('mutable parameter operation requires separate review')
    return assignments


def record_review(text,name):
    values = lex(text)
    starts = [i for i in range(len(values)-1) if values[i][0] == 'record' and values[i+1][0] == name]
    if not starts:
        return dict(kind='NONRECORD_EXCEPTION_REVIEWED_SEPARATELY_NOT_VALUE_ORACLE')
    if len(starts) != 1:
        raise ValueError('one exact bound record declaration required')
    opening = starts[0]+2
    while values[opening][0] != '(':
        opening += 1
    header_end = closing(values,opening,'(',')')
    names = parameters(values[opening+1:header_end])
    begin = header_end+1
    while values[begin][0] != '{': begin += 1
    end = closing(values,begin,'{','}')
    record_text = text[values[begin][1]:values[end][2]]
    assert not re.search(r'\bboolean\s+equals\s*\(',record_text)
    compacts = [i for i in range(begin+1,end-1) if values[i][0] == name and values[i+1][0] == '{']
    if not compacts:
        assert not any(values[i][0] == name and values[i+1][0] == '(' and values[i-1][0] in ('public','protected','private','{',';','}')
            for i in range(begin+1,end-1))
        return dict(kind='IMPLICIT_RECORD_CANONICAL_CONSTRUCTOR_NO_USER_TRANSFORMATION',components=names,
            headerTokenSha256=data.sha(' '.join(v for v,_,_ in values[opening:header_end+1]).encode()))
    assert len(compacts) == 1
    body_begin = compacts[0]+1
    body_end = closing(values,body_begin,'{','}')
    body = text[values[body_begin][2]:values[body_end][1]]
    copies = body_contract(body,names)
    return dict(kind='VALIDATION_AND_SAME_VALUE_OWNERSHIP_COPY' if copies else 'VALIDATION_ONLY_NO_COMPONENT_REASSIGNMENT',
        components=names,sameValueOwnershipCopies=copies,constructorBodySha256=data.sha(body.encode()),
        constructorBodyStartLine=text.count('\n',0,values[body_begin][1])+1,
        constructorBodyEndLine=text.count('\n',0,values[body_end][1])+1,
        noCustomRecordEqualsInSource=True)


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    primary = data.read_checked(data.BASE/'PG10582-constructor-assertion-span-bindings-v1/manifest.json',
        '5d591abfbe83b4d81b5086ceb6081fa04cb4d2e6492225b0938c30b5e198eaa1')
    rows = data.read_checked(data.BASE/'PG10582-constructor-assertion-span-bindings-v1/constructor-bindings.json',primary['rowsSha256'])
    owners = {}
    for row in rows:
        for binding in row['assertionSpanConstructorBindings'].values():
            if binding['mainSourceBinding'] is not None:
                owners[binding['owners'][0]] = binding['mainSourceBinding']
    result = []
    for owner,binding in sorted(owners.items()):
        text = (data.ROOT/binding['source']).read_text()
        assert data.sha(text.encode()) == binding['sourceSha256']
        name = owner.rsplit('$',1)[-1].rsplit('/',1)[-1]
        result.append(dict(owner=owner,**binding,review=record_review(text,name)))
    assert len(result) == 61
    counts = Counter(row['review']['kind'] for row in result)
    assert counts == dict(NONRECORD_EXCEPTION_REVIEWED_SEPARATELY_NOT_VALUE_ORACLE=2,
        IMPLICIT_RECORD_CANONICAL_CONSTRUCTOR_NO_USER_TRANSFORMATION=6,
        VALIDATION_AND_SAME_VALUE_OWNERSHIP_COPY=1,VALIDATION_ONLY_NO_COMPONENT_REASSIGNMENT=52)
    assert next(row for row in result if row['review']['kind']=='VALIDATION_AND_SAME_VALUE_OWNERSHIP_COPY')['owner'].endswith('/FixedServiceIdentity$Value')
    assert body_contract('groups = List.copyOf(groups);',['groups'])
    rejected = 0
    for bad in ('value = 0;','value++;','value.clear();','value = normalize(value);'):
        try:
            body_contract(bad,['value'])
        except ValueError:
            rejected += 1
    assert rejected == 4
    extras = ['src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/semantic/IdValue.java',
        'src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/TypedFieldValues.java']
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'constructor-reviews.json',result)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=primary['source'],invocation=invocation,
        mainOwnersReviewed=61,uniqueMainSources=55,constructorKinds=dict(counts),
        reviewsSha256=data.sha((OUT/'constructor-reviews.json').read_bytes()),
        validationHelperHashes={p:data.sha((data.ROOT/p).read_bytes()) for p in extras},
        metadataNegativeVectors=4,newOracleGap='BUG-1846/YKT1597_FOUR_EXPECTED_EXCEPTION_MESSAGE_FACTORIES',
        allArgumentOriginsOrCaseFixturesQualified=False,providerCallbacksOrRuntimeEnvironmentQualified=False,
        targetCompilation=0,targetClassLoading=0,productTestsExecuted=0,externalActions=0,
        newAccepted=0,wholeG03Accepted=False,formalUpdated=False,effortPercent=None))
    print(dict(actualExit=0,counts=dict(counts),manifestSha256=data.sha((OUT/'manifest.json').read_bytes())))


if __name__ == '__main__':
    main()
