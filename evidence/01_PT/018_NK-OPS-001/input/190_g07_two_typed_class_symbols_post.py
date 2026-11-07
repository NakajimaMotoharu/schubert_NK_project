"""Independent exact field roles, package declarations and original residual multiset."""
from pathlib import Path
from collections import Counter
import datetime
import hashlib
import json
import re
R=Path(__file__).resolve().parents[4]
B=R/'evidence/01_PT/018_NK-OPS-001/evidence'
SRC=B/'PG22328-g07-two-typed-class-symbols-v1'
OUT=B/'PG22332-g07-two-typed-class-symbols-independent-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_bytes())
key=lambda x:tuple(x[k] for k in ['path','ruleId','startLine','endLine','inputSha256'])
def counter_key(text,line):
    field=list(re.finditer(r'^  "targetCounters": ',text,re.M))
    if len(field)!=1:return None
    start=field[0].end();obj,length=json.JSONDecoder().raw_decode(text[start:])
    if not isinstance(obj,dict):return None
    lines=text.splitlines(keepends=True);prefix=sum(len(x) for x in lines[:line-1]);token=re.fullmatch(r'    ("(?:\\.|[^"\\])*"): \{\n?',lines[line-1])
    if not token or not start<=prefix<start+length:return None
    literal=json.loads(token[1])
    return (literal,prefix+token.start(1),prefix+token.end(1)) if literal in obj else None

def main():
    assert not OUT.exists();assert sha(SRC/'manifest.json')=='f030d18a02f46f723d0406d9870e1298cbbce6b9a9440c6e219b496f1e1787ee';m=load(SRC/'manifest.json');assert m['actualExit']==0 and m['additionalFalsePositives']==2 and sha(SRC/'updates.json')==m['updatesSha256'];updates=load(SRC/'updates.json');assert len(updates)==2
    origin=B/'provisional/PG9888-g07-capture-shape-v1';assert sha(origin/'residual-metadata-shapes.json')==m['originalMetadataSha256'];all_rows=load(origin/'residual-metadata-shapes.json');original=Counter(key(x) for x in all_rows);prior=[]
    for slot in ['PG22160-g07-three-public-test-symbols-v1','PG22170-g07-four-selector-symbols-v1','PG22184-g07-two-public-class-references-v2']:
        pm=load(B/slot/'manifest.json');assert sha(B/slot/'updates.json')==pm['updatesSha256'];prior.extend(load(B/slot/'updates.json'))
    old=Counter(key(x) for x in prior);new=Counter(key(x) for x in updates);assert sum(old.values())==9 and sum(new.values())==2 and not old.keys()&new.keys() and all(v==1 and original[k]==1 for k,v in new.items()) and sum((original-old-new).values())==4482
    # Prior current-Jar partial proof made no update and cannot be counted again.
    partial=B/'PG22320-g07-owned-class-byte-provenance-v1';assert load(partial/'manifest.json')['additionalFalsePositives']==0 and not load(partial/'updates.json')
    rule=B/'provisional/PG8979-gitleaks-rule-provenance-v1/manifest.json';assert sha(rule)==m['ruleManifestSha256'];rx=re.compile(load(rule)['rules']['generic-api-key']['regex'],re.ASCII);source_pins={}
    for proof in updates:
        p=R/proof['path'];assert sha(p)==proof['inputSha256'];text=p.read_text();doc=json.loads(text);line=proof['startLine'];matches=[x for x in rx.finditer(text) if text.count('\n',0,x.start(1))+1==line==text.count('\n',0,x.end(1))+1];assert len(matches)==1 and list(matches[0].span(1))==proof['captureCharacterSpan'];capture=matches[0]
        if proof['proofKind']=='TARGET_COUNTERS_TYPED_CLASS_KEY':
            found=counter_key(text,line);assert found is not None;literal,a,z=found;module,relative=literal.split(':',1);assert relative==capture.group(1) and relative.startswith(module+'/');assert set(doc['targetCounters'][literal])=={'LINE','METHOD','CLASS','BRANCH'}
        else:
            assert proof['proofKind']=='WITNESS_TYPED_CLASS_KEY';raw=text.splitlines(keepends=True)[line-1];token=re.fullmatch(r'        "key": ("(?:\\.|[^"\\])*"),\n?',raw);assert token;literal=json.loads(token[1]);prefix=sum(len(x) for x in text.splitlines(keepends=True)[:line-1]);a=prefix+token.start(1);z=prefix+token.end(1);assert literal==capture.group(1)
            records=[v for v in doc['actualWitnesses']['witnesses'] if v['key']==literal];assert len(records)==1;record=records[0];module=record['module'];relative=literal;assert relative.startswith(module+'/')
            witness=record['class'].replace('.','/');wp='src/schubert-nk-'+module+'/src/test/java/'+witness+'.java';assert not any(v in wp for v in ['RootFailedStartRecoveryTest','RootFailedStartPairRecoveryTest','SnapshotKeyCloseWitness','pg9892','private']);witness_text=(R/wp).read_text();package,simple=witness.replace('/','.').rsplit('.',1);assert re.search(r'^package\s+'+re.escape(package)+r';',witness_text,re.M) and re.search(r'\bclass\s+'+re.escape(simple)+r'\b',witness_text) and re.search(r'\bvoid\s+'+re.escape(record['method'])+r'\s*\(',witness_text);source_pins[wp]=sha(R/wp)
        assert [a,z]==proof['tokenCharacterSpan'] and a+1<=capture.start(1)<capture.end(1)<=z-1
        internal='dev/codex/schubert/nk/'+relative;path='src/schubert-nk-'+module+'/src/main/java/'+internal+'.java';assert path==proof['declarationPath'];assert sha(R/path)==proof['declarationSourceSha256'];java=(R/path).read_text();package,simple=internal.replace('/','.').rsplit('.',1);assert re.search(r'^package\s+'+re.escape(package)+r';',java,re.M);declaration=re.search(r'^public\s+(?:(?:final|sealed|abstract)\s+)?class\s+'+re.escape(simple)+r'\b',java,re.M);assert declaration and [java.count('\n',0,declaration.start())+1]==proof['declarationLines'];source_pins[path]=sha(R/path)
    sample='{\n  "targetCounters": {\n    "api:api/Foo": {\n      "LINE": 1\n    }\n  }\n}'
    assert counter_key(sample,3)[0]=='api:api/Foo' and counter_key(sample.replace('targetCounters','other'),3) is None and counter_key(sample,4) is None and counter_key('{\n  "targetCounters": [\n    "api:api/Foo"\n  ]\n}',3) is None
    assert len(m['retainedUnclassified'])==1;retained=m['retainedUnclassified'][0];assert not any(x['path']==retained['path'] for x in updates) and any(x['path']==retained['path'] and x['startLine']==retained['line'] for x in all_rows)
    OUT.mkdir();result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),producerManifest=dict(path=str((SRC/'manifest.json').relative_to(R)),sha256=sha(SRC/'manifest.json')),sourcePins=source_pins,typedReferences=2,retainedCandidate=1,newFalsePositives=2,remainingUnclassified=4482,previousNineUpdatesPreserved=True,minifiedPartial28NotCounted=True,negativeChecks=4,productTestsExecuted=0,scannerExecuted=False,targetsExecuted=False,operatorSourceReadSetExpanded=False,valuesOrValueHashesWritten=False,newAccepted=0,currentWholeG07Qualified=False,effortRate=None,verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))))
    (OUT/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,classified=2,remaining=4482,manifestSha256=sha(OUT/'manifest.json'))))
if __name__=='__main__':main()
