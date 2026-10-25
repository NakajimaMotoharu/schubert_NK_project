"""Exact existing case-token/spec-row candidates only; never infer oracle validity or test PASS."""
from collections import Counter,defaultdict
import datetime as dt
import json
from pathlib import Path
import re
import subprocess
import explicit_case_row_inputs as data
from host_tool_invocation import capture,verify

ROOT=data.ROOT;BASE=data.BASE;SOURCE=data.SOURCE
OUT=BASE/'PG9598-explicit-case-row-candidates-v1'
TOKEN=re.compile(r'([A-Za-z]+[0-9]{3})(?=[A-Z_]|$)')
IDS=re.compile(r'(?<![A-Za-z0-9-])([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*[0-9]{3})(?![A-Za-z0-9-])')
CLASS=re.compile(r'^\s*(?:public\s+)?(?:(?:final|abstract|sealed|non-sealed)\s+)*class\s+',re.M)

def header_doc_refs(text):
    declaration=CLASS.search(text)
    if declaration is None:return []
    comments=re.findall(r'/\*\*([\s\S]*?)\*/',text[:declaration.start()])
    if not comments:return []
    return sorted({int(x) for x in re.findall(r'(?<![A-Za-z0-9])(\d{3,4})(?=[/_ :])',comments[-1])})

def choose(matches,refs):
    selected=[r for r in matches if r['specNumber'] in refs] if refs else matches
    if not selected:return ('EXPLICIT_DOCREF_HAS_NO_MATCHING_ROW' if matches and refs else 'NO_EXPLICIT_SPEC_ROW'),[]
    if len(selected)>1:return 'MULTIPLE_SPEC_ROWS_REVIEW_REQUIRED',selected
    return ('UNIQUE_SOURCE_DOCREF_AND_CASE_TOKEN_CANDIDATE' if refs else 'UNIQUE_GLOBAL_CASE_TOKEN_CANDIDATE'),selected

def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    methods=data.methods();corpus=data.corpus();by_token=defaultdict(list);spec_rows=[]
    tokens={match.group(1).upper() for row in methods if (match:=TOKEN.match(row['method']))}
    assert len(tokens)==3204
    for meta,text in corpus:
        prefix=Path(meta['path']).name.split('_',1)[0];number=int(prefix) if prefix.isdigit() else None
        for line_number,line in enumerate(text.splitlines(),1):
            if not line.startswith('|'):continue
            cell=line.split('|')[1]
            if any(s in cell for s in ('～','..','…','~')) or re.search(r'\d{3}\s*[-–—]\s*\d',cell):continue
            for test_id in sorted(set(IDS.findall(cell))):
                matching=[token for token in tokens if test_id==token or test_id.endswith('-'+token)]
                for token in matching:
                    ref=dict(specPath=meta['path'],specSha256=meta['sha256'],specNumber=number,line=line_number,
                      rowSha256=data.data.sha(line.encode()),testId=test_id,caseToken=token)
                    by_token[token].append(ref);spec_rows.append(ref)
    cache={};rows=[];counts=Counter()
    for method in methods:
        path=method['path']
        if path not in cache:
            raw=(ROOT/path).read_bytes();assert data.data.sha(raw)==method['sourceSha256']
            cache[path]=header_doc_refs(raw.decode())
        token=TOKEN.match(method['method']);refs=cache[path]
        if token:
            value=token.group(1).upper();status,selected=choose(by_token[value],refs)
        else:value=None;status='NO_STRICT_METHOD_NAME_CASE_TOKEN';selected=[]
        counts[status]+=1
        rows.append(dict(methodDeclarationKey=method['methodDeclarationKey'],caseToken=value,sourceHeaderDocRefs=refs,
          referenceStatus=status,specRowCandidates=selected,oracleSemanticsQualified=False,productExecuted=False,
          originalMethodBindingManifest='PG9592-current-test-method-post-v1',candidateIsNotAnInventedTestId=True))
    assert len(rows)==5622 and sum(r['caseToken'] is not None for r in rows)==3344
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)==b''
    verify(invocation);OUT.mkdir()
    data.data.write(OUT/'spec-corpus.json',[meta for meta,_ in corpus]);data.data.write(OUT/'explicit-spec-rows.json',spec_rows)
    data.data.write(OUT/'method-spec-row-candidates.json',rows)
    result=dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
      specSha256=data.SPEC_SHA,corpusGitHead=data.HEAD,corpusDocuments=len(corpus),explicitSpecRows=len(spec_rows),
      methodDeclarations=5622,methodNameCaseTokenCandidates=3344,uniqueCaseTokens=3204,referenceCounts=dict(counts),
      corpusSha256=data.data.sha((OUT/'spec-corpus.json').read_bytes()),specRowsSha256=data.data.sha((OUT/'explicit-spec-rows.json').read_bytes()),
      candidatesSha256=data.data.sha((OUT/'method-spec-row-candidates.json').read_bytes()),
      rangeOrAliasExpansion=False,oracleSemanticsQualified=False,productTestsExecuted=0,newTestIds=0,newMain=0,
      coverage=None,formalUpdated=False,newAccepted=0,effortPercent=None,wholeG13Accepted=False,whole451Accepted=False)
    data.data.write(OUT/'manifest.json',result)
    print(json.dumps(dict(actualExit=0,corpusDocuments=len(corpus),referenceCounts=dict(counts))))
    print('manifestSha256='+data.data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
