"""Read-only128 unchanged-source expected constructor sites; no Production execution."""
from collections import Counter
from pathlib import Path
import re
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX

SOURCE = '6612747b7a5492e5c49647d85cfc2dcbe6d75c9f'
OUT = data.BASE/'PG10520-constructor-carrier-review-v3'
TYPES = {
    'CleanupCounts':'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/CleanupCounts.java',
    'BatchStepResult':'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/BatchStepResult.java',
    'OutboxDispatchReport':'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/outbound/OutboxDispatchReport.java',
    'PagedResponseData':'src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/common/PagedResponseData.java'}
ENUMS = {'SUCCESS','WARNING','FAILED','SKIPPED','NONE','ALREADY_SUCCESSFUL','BACKUP_UNAVAILABLE','PROTECTED_RECORDS',
    'ABANDONED','DATABASE_FAILURE','COMMAND_FAILURE','SAFETY_FAILURE','IO_FAILURE','TIMEOUT','INTERRUPTED'}
ORIGINAL8 = {'NotificationControllerTest','QuestionControllerTest','ApiSessionInvalidTest','ErrorMvcTest',
    'ScenarioControllerTest','SessionAccessFailureTest','SessionLoginHandlerTest','SessionSecurityContextTest'}


def lex(text):
    return [(m.group(),m.start(),m.end()) for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]


def body_at(text,start):
    depth = 1
    for token,_,end in lex(text[start:]):
        if token == '{': depth += 1
        if token == '}': depth -= 1
        if depth == 0: return text[start:start+end-1]
    raise ValueError('complete constructor block required')


def constructor_contract(text,name):
    header = re.search(r'public\s+record\s+'+name+r'\s*\((.*?)\)\s*(?:implements[^{}]+)?\{',text,re.S)
    compact = re.search(r'public\s+'+name+r'\s*\{',text)
    if not header or not compact: raise ValueError('exact named record compact constructor required')
    parameters = [p.strip().split()[-1] for p in header[1].split(',')]
    body = body_at(text,compact.end())
    values = ' '.join(t for t,_,_ in lex(body))
    for parameter in parameters:
        if re.search(r'\b'+parameter+r'\s*(?:=(?!=)|\+\+|--|[+\-*/]=)',body):
            raise ValueError('expected carrier must not transform any component')
    if re.search(r'\bthis\s*\.',body): raise ValueError('no custom field mutation')
    calls = re.findall(r'\b([A-Za-z_$][\w$]*)\s*\(',values)
    if set(calls)-{'if','IllegalArgumentException','requireNonNull','requireUnsignedRange','allows'}:
        raise ValueError('unreviewed constructor behavior')
    return dict(components=parameters,constructorTokenSha256=data.sha(values.encode()),
        componentReassignments=0,purpose='VALIDATION_ONLY_COMPONENT_PRESERVATION_NO_ENCODING_NORMALIZATION_OR_DERIVATION')


def first_argument(text,row):
    values = lex(text)
    matches = []
    pairs = {')':'(',']':'[','}':'{'}
    for index,(name,_,_) in enumerate(values[:-2]):
        if name != row['assertion'] or values[index+1][0] != '(':
            continue
        begin = index+2
        start = values[begin][1]
        if text.count('\n',0,start)+1 != row['line']:
            continue
        nesting = []
        for i in range(begin,len(values)):
            value = values[i][0]
            if value == ',' and not nesting:
                end = values[i-1][2]
                if data.sha(text[start:end].encode()) == row['expectedExpressionSha256']:
                    matches.append(values[begin:i])
                break
            if value in ('(','[','{'):
                nesting.append(value)
            elif value in pairs:
                if not nesting or nesting.pop() != pairs[value]:
                    break
    if len(matches) != 1:
        raise ValueError('unique original expected-expression line and byte digest required')
    return matches[0]


def argument_names(expression):
    names = []
    for i,(value,_,_) in enumerate(expression):
        if not re.fullmatch(r'[A-Za-z_$][\w$]*',value): continue
        if value in set(TYPES)|ENUMS|{'new','true','false','null','Optional','Math','Status','Reason','L'}: continue
        if value in {'of','min'} and i >= 2 and expression[i-1][0] == '.' and expression[i-2][0] in {'Optional','Math'}: continue
        names.append(value)
    return sorted(set(names))


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    original = data.read_checked(data.BASE/'PG10252-remaining-oracle-sites-v1/manifest.json',
        '745d934fbb1860218efc7b5bbdbffd36d8cc9985b26a911a59ca7d50c253c72f')
    sites = data.read_checked(data.BASE/'PG10252-remaining-oracle-sites-v1/sites.json',original['sitesJsonSha256'])
    normal = data.read_checked(data.BASE/'PG10508-anm-type-name-compile-v1/manifest.json',
        'bc2c2ee9ff267ab6ea56f33df42b0272636cd928c23cdb3cc9b33bf1db3773c5')
    assert normal['source'] == SOURCE and normal['actualExit'] == 0 and normal['testsExecuted'] == 0
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src'],cwd=data.ROOT) == b''
    subjects = {}
    for name,path in TYPES.items():
        text = (data.ROOT/path).read_text()
        assert data.sha(text.encode()) == normal['begin']['inputHashes'][path]
        subjects[name] = dict(path=path,sha256=data.sha(text.encode()),contract=constructor_contract(text,name))
    selected = []
    cache = {}
    skipped = 0
    for row in sites:
        if not set(TYPES)&set(row['expectedConstructorTypes']): continue
        path = row['path']
        if Path(path).stem in ORIGINAL8: continue
        if path not in cache: cache[path] = (data.ROOT/path).read_text()
        text = cache[path]
        if data.sha(text.encode()) != row['sourceSha256']:
            skipped += 1
            continue
        assert row['sourceSha256'] == normal['begin']['inputHashes'][path]
        additional = sorted(set(row['expectedConstructorTypes']) - set(TYPES))
        assert set(row['expectedMethodSelectors']) <= {'Optional.of','Math.min'}
        for name in set(row['expectedConstructorTypes']) & set(TYPES):
            assert not re.search(r'\b(?:class|record|interface|enum)\s+'+name+r'\b',text)
            subject = (data.ROOT/TYPES[name]).read_text()
            package = re.search(r'\bpackage\s+([\w.]+);',subject)[1]
            assert 'import '+package+'.'+name+';' in text or 'package '+package+';' in text
        expression = first_argument(text,row)
        unresolved = argument_names(expression)
        selected.append(dict(**row,constructorClassification='NON_TRANSFORMING_CARRIER_NOT_SUT_OUTPUT_ENCODER',
            additionalConstructorTypesNotReviewed=additional,
            expectedTokenSha256=data.sha(' '.join(v for v,_,_ in expression).encode()),
            unresolvedArgumentNames=unresolved,
            argumentQualification='VARIABLE_ARGUMENT_PROVENANCE_REVIEW_REQUIRED' if unresolved else 'EXPLICIT_LITERAL_ENUM_CARRIER_ARGUMENTS',
            originalDynamicPtStatus='NOT_EXECUTED_BY_THIS_REVIEW'))
    assert sum(bool(r['additionalConstructorTypesNotReviewed']) for r in selected) == 5
    assert len(selected) == 128 and len({r['path'] for r in selected}) == 21
    span_vectors = []
    for sample in ('assertEquals(new CleanupCounts(1, 1, 0), actual);',
                   'assertEquals(\n  new CleanupCounts(1, 1, 0), actual);'):
        expression = 'new CleanupCounts(1, 1, 0)'
        row = dict(assertion='assertEquals',line=sample.count('\n',0,sample.index(expression))+1,
            expectedExpressionSha256=data.sha(expression.encode()))
        assert first_argument(sample,row)
        for field,bad in (('line',99),('expectedExpressionSha256','0'*64)):
            try: first_argument(sample,dict(row,**{field:bad}))
            except ValueError: span_vectors.append(dict(multiline='\n' in sample,mutation=field))
            else: raise AssertionError('wrong expected-expression provenance accepted')
    assert len(span_vectors) == 4
    negatives = []
    for name,subject in subjects.items():
        path = TYPES[name]
        text = (data.ROOT/path).read_text()
        compact = re.search(r'public\s+'+name+r'\s*\{',text)
        field = subject['contract']['components'][0]
        damaged = text[:compact.end()]+'\n'+field+' = '+field+';\n'+text[compact.end():]
        try: constructor_contract(damaged,name)
        except ValueError: negatives.append(dict(type=name,mutation='component-reassignment'))
        else: raise AssertionError('transforming expected carrier accepted')
    assert len(negatives) == 4
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'sites.json',selected)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        subjects=subjects,syntaxSitesReviewed=128,consumerSources=21,
        subjectCounts=dict(Counter(v for r in selected for v in r['expectedConstructorTypes'])),
        additionalConstructorSitesNotReviewed=5,expectedExpressionByteDigestsMatched=128,
        sitesSha256=data.sha((OUT/'sites.json').read_bytes()),sourceHashes={r['path']:r['sourceSha256'] for r in selected},
        explicitLiteralEnumArgumentSites=sum(not r['unresolvedArgumentNames'] for r in selected),
        variableArgumentSites=sum(bool(r['unresolvedArgumentNames']) for r in selected),
        changedSourceSitesSkipped=skipped,metadataNegativeVectors=negatives,expressionSpanNegativeVectors=span_vectors,
        consumerVariableProvenanceFullyResolved=False,wholeOracleIndependenceAccepted=False,
        productTestsExecuted=0,targetCompilation=0,targetClassLoading=0,externalActions=0,
        newDefectsConfirmed=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(dict(actualExit=0,sites=128,literal= sum(not r['unresolvedArgumentNames'] for r in selected),
        variable=sum(bool(r['unresolvedArgumentNames']) for r in selected),manifestSha256=data.sha((OUT/'manifest.json').read_bytes())))


if __name__ == '__main__':
    main()
