"""Independent source SQL equivalence only; existing independent Test literals remain the PT oracle."""
from collections import Counter
from pathlib import Path
import datetime
import hashlib
import json
import re

r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';before=b/'evidence/PG36868-ssc450-sql-source-manufacture-v1'
manifest=json.loads((before/'manifest.json').read_text());base=r/'src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/migration'
out=b/'evidence/PG36870-ssc450-sql-equivalence-v1';assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def expressions(text):
    result=[];quote=False;escape=False;depth=0;start=0
    for i,c in enumerate(text):
        if quote:
            if escape:escape=False
            elif c=='\\':escape=True
            elif c=='"':quote=False
        elif c=='"':quote=True
        elif c=='(':depth+=1
        elif c==')':depth-=1
        elif c==',' and depth==0:result.append(text[start:i].strip());start=i+1
    result.append(text[start:].strip());assert not quote and depth==0
    return result
def constants(text):
    values={}
    for match in re.finditer(r'private static final String (\w+)\s*=\s*((?:"(?:\\.|[^"\\])*"\s*(?:\+\s*)?)+);',text,re.S):
        values[match.group(1)]=''.join(json.loads(x) for x in re.findall(r'"(?:\\.|[^"\\])*"',match.group(2)))
    return values
def evaluate(expression,known):
    token=re.compile(r'\s*("(?:\\.|[^"\\])*"|[A-Za-z_]\w*|\+)')
    offset=0;parts=[];need_value=True
    while offset<len(expression):
        if expression[offset:].strip()=='':break
        match=token.match(expression,offset);assert match,'nonconstant SQL expression'
        value=match.group(1);offset=match.end()
        if need_value:
            assert value!='+';parts.append(json.loads(value) if value.startswith('"') else known[value])
        else:assert value=='+'
        need_value=not need_value
    assert not need_value and parts
    return ''.join(parts)
def list_values(text,field):
    match=re.search(r'private static final List<String> '+field+r'\s*=\s*List\.of\((.*?)\);',text,re.S);assert match
    return [evaluate(x,constants(text)) for x in expressions(match.group(1))]
def call_arguments(text):
    calls=[]
    for match in re.finditer(r'\b(?:statement|connection)\.(executeQuery|executeUpdate|executeLargeUpdate|prepareStatement)\(',text):
        i=match.end();start=i;depth=1;quote=False;escape=False
        while depth:
            c=text[i]
            if quote:
                if escape:escape=False
                elif c=='\\':escape=True
                elif c=='"':quote=False
            elif c=='"':quote=True
            elif c=='(':depth+=1
            elif c==')':depth-=1
            i+=1
        expression=text[start:i-1].strip()
        if expression:calls.append(dict(operation=match.group(1),sql=evaluate(expression,constants(text))))
    return calls
old_corpus=json.loads((before/'sql-corpus-equivalence-inputs.json').read_text());rows=[]
for path in manifest['sourceHashesAfter']:
    name=Path(path).stem;old=(before/(name+'-before.java.txt')).read_text();new=(r/path).read_text()
    if name in ['MigrationMasterColumnVerifier','MigrationMasterConstraintVerifier','MigrationMasterContentVerifier']:
        expected=[dict(operation='executeQuery',sql=value) for value in list_values(old,'QUERIES')]
    elif name=='MigrationMasterReferenceVerifier':
        expected=[dict(operation='executeQuery',sql=value) for field in ['COUNTS','INSPECTIONS'] for value in list_values(old,field)]
    elif name=='MigrationMasterFinalizer':
        identity=list_values(old,'IDENTITY_TABLES');analyze=list_values(old,'ANALYZE_TABLES')
        constraint=re.search(r'statement\.executeUpdate\(\s*("(?:\\.|[^"\\])*")',old);assert constraint
        expected=[dict(operation='executeUpdate',sql=json.loads(constraint.group(1)))]
        expected.extend(dict(operation='executeQuery',sql='SELECT COALESCE(MAX(id),0) FROM schubert.'+t) for t in identity)
        expected.extend(dict(operation='prepareStatement',sql="SELECT pg_catalog.setval(pg_catalog.pg_get_serial_sequence('schubert."+t+"', 'id'), ?, ?)") for t in identity)
        expected.extend(dict(operation='executeUpdate',sql='ANALYZE schubert.'+t) for t in analyze)
    else:
        assert name=='AssetStagingTables';expected=[]
        for table in old_corpus[name]:
            expected.extend([dict(operation='executeUpdate',sql=table['prepare']),
               dict(operation='executeQuery',sql=table['targetCount']),
               dict(operation='executeQuery',sql=table['stagedCount']),
               dict(operation='executeLargeUpdate',sql=table['insert'])])
    actual=call_arguments(new)
    key=lambda x:(x['operation'],x['sql'])
    assert Counter(map(key,actual))==Counter(map(key,expected)),name+' exact SQL/operator corpus'
    # Preserve declared public APIs exactly; private operation representation intentionally changes.
    public=lambda t:re.findall(r'  public (?:[^\{]|\n)*?\{',t)
    normalize=lambda values:[' '.join(x.split()) for x in values]
    assert normalize(public(old))==normalize(public(new)),name+' public API'
    assert new.count('SuppressFBWarnings')==old.count('SuppressFBWarnings')
    rows.append(dict(path=path,beforeSha256=sha(before/(name+'-before.java.txt')),afterSha256=sha(r/path),
       sqlCallsites=len(actual),corpusSha256=hashlib.sha256(json.dumps(sorted(map(key,actual))).encode()).hexdigest(),
       sqlAndOperationCorpusExact=True,declaredPublicApiExact=True,
       privateNoCodeInterfaces=new.count('private interface Sql'),calls=actual))
assert len(rows)==6 and all(sha(r/path)==h for path,h in manifest['originalTestSourceHashes'].items())
out.mkdir();(out/'sql-corpus-and-public-api.json').open('x').write(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
result=dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceBefore=manifest['sourceBefore'],
   sourceIsUncommittedCandidate=True,ssc='SSC450',mainSources=6,
   sqlCallsites=sum(x['sqlCallsites'] for x in rows),newTrueNoCodeInterfaces=sum(x['privateNoCodeInterfaces'] for x in rows),
   originalTestSourceHashes=manifest['originalTestSourceHashes'],originalTestSourcesUnchanged=True,
   expectedValuesForPt='UNCHANGED_INDEPENDENT_TEST_LITERALS_AND_APPROVED_DDL_NOT_THIS_SOURCE_EQUIVALENCE',
   productionMethodsInvoked=0,productTestsExecuted=0,formalUpdated=False,
   pending=['closed whole160/source closure','Root compile/static','actual tests/raw counters','binary API/unchanged bytes','independent post'])
(out/'manifest.json').open('x').write(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,Main6=True,sqlCallsites=result['sqlCallsites'],
   NoCodeInterfaces=result['newTrueNoCodeInterfaces'],original160TestsUnchanged=True)))
