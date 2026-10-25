"""Independently rebuild existing spec-row references; no expectation semantics or target tests."""
from collections import Counter,defaultdict
import copy
import datetime as dt
import json
from pathlib import Path
import re
import subprocess
import explicit_case_row_inputs as data
from host_tool_invocation import capture,verify

ROOT=data.ROOT;BASE=data.BASE;SOURCE=data.SOURCE
SUBJECT=BASE/'PG9598-explicit-case-row-candidates-v1'
SUBJECT_SHA='538aedc37867bbc02c373dafde7155c77383c711ec51fb0f17786b123fdd1183'
OUT=BASE/'PG9600-explicit-case-row-post-v1'

def case_token(name):
    at=0
    while at<len(name) and ('A'<=name[at]<='Z' or 'a'<=name[at]<='z'):at+=1
    if at==0 or len(name)<at+3 or any(c not in '0123456789' for c in name[at:at+3]):return None
    end=at+3
    if end<len(name) and not ('A'<=name[end]<='Z' or name[end]=='_'):return None
    return name[:end].upper()

def refs_from_header(source):
    lexer=re.compile(r'//[^\r\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|[A-Za-z_$][A-Za-z0-9_$]*|.',re.S)
    comment=None;found=False
    for match in lexer.finditer(source):
        token=match.group()
        if token=='class':found=True;break
        if token.startswith('/**'):comment=token[3:-2]
    if not found or comment is None:return []
    values=set()
    for match in re.finditer(r'[0-9]+',comment):
        start,end=match.span();before=comment[start-1] if start else '';after=comment[end] if end<len(comment) else ''
        if len(match.group()) in (3,4) and (not before or before not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789') and after and after in '/_ :':
            values.add(int(match.group()))
    return sorted(values)

def ids_in_cell(cell):
    if any(x in cell for x in ('～','..','…','~')) or re.search(r'[0-9]{3}\s*[-–—]\s*[0-9]',cell):return []
    # Scan complete ASCII alphanumeric/hyphen words, not producer's ID regex.
    words=re.findall(r'[A-Za-z0-9-]+',cell)
    return sorted({w for w in words if w and 'A'<=w[0]<='Z' and len(w)>=4 and w[-3:].isdigit()
      and all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-' for c in w)
      and all(part for part in w.split('-'))})

def selection(matches,refs):
    considered=[]
    for row in matches:
        if not refs or row['specNumber'] in refs:considered.append(row)
    if len(considered)>1:return 'MULTIPLE_SPEC_ROWS_REVIEW_REQUIRED',considered
    if len(considered)==1:return ('UNIQUE_SOURCE_DOCREF_AND_CASE_TOKEN_CANDIDATE' if refs else 'UNIQUE_GLOBAL_CASE_TOKEN_CANDIDATE'),considered
    return ('EXPLICIT_DOCREF_HAS_NO_MATCHING_ROW' if refs and matches else 'NO_EXPLICIT_SPEC_ROW'),[]

def validate(observed,expected):
    if observed!=expected:raise ValueError('exact method/case/spec-row reference required, not oracle or PASS')

def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    c=data.data;subject=c.read_checked(SUBJECT/'manifest.json',SUBJECT_SHA);assert subject['actualExit']==0 and subject['source']==SOURCE
    methods=data.methods();corpus=c.read_checked(SUBJECT/'spec-corpus.json',subject['corpusSha256'])
    original_rows=c.read_checked(SUBJECT/'explicit-spec-rows.json',subject['specRowsSha256'])
    observed=c.read_checked(SUBJECT/'method-spec-row-candidates.json',subject['candidatesSha256'])
    listing=subprocess.check_output(['git','ls-tree','-r','--name-only','-z',data.HEAD,'--','evidence/01_PT'],cwd=ROOT)
    expected_paths=sorted(p for p in listing.decode().split('\0') if p and len(Path(p).parts)==4 and p.endswith('.md') and '仕様' in Path(p).name)
    assert [r['path'] for r in corpus]==expected_paths and len(corpus)==1188
    raw=subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=''.join(data.HEAD+':'+r['path']+'\n' for r in corpus).encode())
    cursor=0;texts={}
    for row in corpus:
        end=raw.index(b'\n',cursor);blob,kind,size=raw[cursor:end].split();cursor=end+1;size=int(size)
        body=raw[cursor:cursor+size];assert raw[cursor+size:cursor+size+1]==b'\n';cursor+=size+1
        assert blob.decode()==row['gitBlob'] and kind==b'blob' and len(body)==row['bytes']==size and c.sha(body)==row['sha256']
        assert (ROOT/row['path']).read_bytes()==body;texts[row['path']]=body.decode()
    assert cursor==len(raw)
    tokens={value for method in methods if (value:=case_token(method['method'])) is not None};assert len(tokens)==3204
    spec_rows=[];by_token=defaultdict(list)
    for meta in corpus:
        prefix=Path(meta['path']).name.partition('_')[0];number=int(prefix) if prefix.isdigit() else None
        for line_number,line in enumerate(texts[meta['path']].splitlines(),1):
            if not line.startswith('|'):continue
            cell=line.partition('|')[2].partition('|')[0]
            for test_id in ids_in_cell(cell):
                for token in sorted(tokens):
                    if test_id!=token and not test_id.endswith('-'+token):continue
                    row=dict(specPath=meta['path'],specSha256=meta['sha256'],specNumber=number,line=line_number,
                      rowSha256=c.sha(line.encode()),testId=test_id,caseToken=token)
                    spec_rows.append(row);by_token[token].append(row)
    validate(original_rows,spec_rows)
    cache={};expected=[];counts=Counter()
    for method in methods:
        path=method['path']
        if path not in cache:
            text=(ROOT/path).read_bytes();assert c.sha(text)==method['sourceSha256'];cache[path]=refs_from_header(text.decode())
        token=case_token(method['method']);refs=cache[path]
        if token is None:status='NO_STRICT_METHOD_NAME_CASE_TOKEN';selected=[]
        else:status,selected=selection(by_token[token],refs)
        counts[status]+=1
        expected.append(dict(methodDeclarationKey=method['methodDeclarationKey'],caseToken=token,sourceHeaderDocRefs=refs,
          referenceStatus=status,specRowCandidates=selected,oracleSemanticsQualified=False,productExecuted=False,
          originalMethodBindingManifest='PG9592-current-test-method-post-v1',candidateIsNotAnInventedTestId=True))
    validate(observed,expected);assert dict(counts)==subject['referenceCounts']
    # Handwritten edge vectors: no aliases/range expansion or global fallback from a wrong docref.
    assert case_token('apiStop001')=='APISTOP001' and case_token('apiStop001Literal')=='APISTOP001'
    assert case_token('apiStop001_lower')=='APISTOP001' and case_token('apiStop001lower') is None
    assert case_token('apiStop0011') is None and case_token('headerNormal') is None
    assert ids_in_cell('`PT-OPS-APISTOP001`')==['PT-OPS-APISTOP001']
    assert ids_in_cell('APISTOP001..018')==[] and ids_in_cell('APISTOP001～APISTOP018')==[]
    assert refs_from_header('/** 1870/APISTOP001..018 */ final class T {}')==[1870]
    assert refs_from_header('class T { String s="1870/APISTOP001"; }')==[]
    fixture=[dict(specNumber=1870),dict(specNumber=1872)]
    assert selection(fixture,[1870])==('UNIQUE_SOURCE_DOCREF_AND_CASE_TOKEN_CANDIDATE',[fixture[0]])
    assert selection(fixture,[9999])==('EXPLICIT_DOCREF_HAS_NO_MATCHING_ROW',[])
    rejected=[]
    for label,edit in (('missing',lambda x:x.pop()),('duplicate',lambda x:x.append(copy.deepcopy(x[0]))),
      ('case-token',lambda x:x[0].update(caseToken='INVENTED001')),('source-docref',lambda x:x[0].update(sourceHeaderDocRefs=[9999])),
      ('oracle-invented',lambda x:x[0].update(oracleSemanticsQualified=True)),('execution-invented',lambda x:x[0].update(productExecuted=True)),
      ('method',lambda x:x[0].update(methodDeclarationKey='foreign')),('status',lambda x:x[0].update(referenceStatus='PASS'))):
        changed=copy.deepcopy(expected);edit(changed)
        try:validate(changed,expected)
        except ValueError:rejected.append(label)
        else:raise AssertionError('invalid candidate reference accepted')
    verify(invocation);OUT.mkdir()
    value=dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
      subjectManifestSha256=SUBJECT_SHA,specSha256=data.SPEC_SHA,corpusGitHead=data.HEAD,
      independentCorpusDocuments=1188,independentMethodDeclarations=5622,referenceCounts=dict(counts),
      literalEdgeVectors=13,metadataCounterexamples=rejected,originalCandidatesSha256=subject['candidatesSha256'],
      oracleSemanticsQualified=False,productTestsExecuted=0,newTestIds=0,newMain=0,coverage=None,
      formalUpdated=False,newAccepted=0,effortPercent=None,wholeG13Accepted=False,whole451Accepted=False)
    c.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,referenceCounts=dict(counts))))
    print('manifestSha256='+c.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
