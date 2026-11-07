"""Two public typed class-reference captures; third document candidate remains unclassified."""
from pathlib import Path
import datetime
import hashlib
import json
import re
R=Path(__file__).resolve().parents[4]
B=R/'evidence/01_PT/018_NK-OPS-001/evidence'
OUT=B/'PG22328-g07-two-typed-class-symbols-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
def main():
    assert not OUT.exists();origin=B/'provisional/PG9888-g07-capture-shape-v1';assert sha(origin/'manifest.json')=='6043b800e9bd89d1fff646dbb7dda064a78ec028a4730e6903cba9c7380871eb';assert sha(origin/'residual-metadata-shapes.json')==load(origin/'manifest.json')['residualMetadataSha256'];pending=load(origin/'residual-metadata-shapes.json')
    rule=B/'provisional/PG8979-gitleaks-rule-provenance-v1/manifest.json';assert sha(rule)=='97b57201394a789a6871fa2f73b6521d71e48e5452ff2b426a6e23e4ca580c8a';rx=re.compile(load(rule)['rules']['generic-api-key']['regex'],re.ASCII);proofs=[]
    for slot,line,role in [('PG3416-failure-graph-scope',418,'WITNESS_TYPED_CLASS_KEY'),('PG5752-exception17',32,'TARGET_COUNTERS_TYPED_CLASS_KEY')]:
        p=B/'provisional'/slot/'manifest.json';name=str(p.relative_to(R));rows=[x for x in pending if x['path']==name and x['startLine']==x['endLine']==line];assert len(rows)==1 and sha(p)==rows[0]['inputSha256'] and rows[0]['uniqueExactCaptureCount']==1
        text=p.read_text();doc=json.loads(text);matches=[x for x in rx.finditer(text) if text.count('\n',0,x.start(1))+1==line==text.count('\n',0,x.end(1))+1];assert len(matches)==1;match=matches[0]
        current_line=text.splitlines(keepends=True)[line-1];prefix=sum(len(v) for v in text.splitlines(keepends=True)[:line-1])
        strings=list(re.finditer(r'"(?:\\.|[^"\\])*"',current_line));assert len(strings)==(2 if role=='WITNESS_TYPED_CLASS_KEY' else 1)
        token=strings[-1];literal=json.loads(token.group());token_start=prefix+token.start();token_end=prefix+token.end();assert token_start+1<=match.start(1)<match.end(1)<=token_end-1
        if role=='WITNESS_TYPED_CLASS_KEY':
            entries=[x for x in doc['actualWitnesses']['witnesses'] if x['key']==literal];assert len(entries)==1;entry=entries[0];module=entry['module'];relative=literal
            internal='dev/codex/schubert/nk/'+relative;assert relative.startswith(module+'/')
            witness=entry['class'].replace('.','/');assert witness.startswith('dev/codex/schubert/nk/') and witness.endswith('Test')
            witness_path='src/schubert-nk-'+module+'/src/test/java/'+witness+'.java';assert not any(v in witness_path for v in ['RootFailedStartRecoveryTest','RootFailedStartPairRecoveryTest','SnapshotKeyCloseWitness','pg9892','private'])
            witness_java=(R/witness_path).read_text();wp,ws=witness.replace('/','.').rsplit('.',1);assert re.search(r'^package\s+'+re.escape(wp)+r';',witness_java,re.M);assert re.search(r'\bclass\s+'+re.escape(ws)+r'\b',witness_java)
            assert re.search(r'\bvoid\s+'+re.escape(entry['method'])+r'\s*\(',witness_java)
            assert match.group(1)==literal and re.fullmatch(r'[a-z]+(?:/[A-Za-z_$][\w$]*)+',literal)
            typed_role='actualWitnesses.witnesses[].key is Main target, class/method are a separately declared Test witness; no Main-from-Test-name inference or execution credit'
        else:
            parsed=re.fullmatch(r'(api|web|batch|bootstrap|protocol|storage):([A-Za-z_$][\w$]*(?:/[A-Za-z_$][\w$]*)+)',literal);assert parsed;module,relative=parsed.groups();assert relative.startswith(module+'/') and match.group(1)==relative
            internal='dev/codex/schubert/nk/'+relative;counter=doc['targetCounters'][literal];assert set(counter)=={'BRANCH','CLASS','LINE','METHOD'} and all(set(x)=={'covered','missed'} and all(type(n) is int and n>=0 for n in x.values()) for x in counter.values())
            typed_role='targetCounters object key with explicit module and class namespace; counter result not acceptance'
        outer,*nested=internal.split('$');assert not nested
        source='src/schubert-nk-'+module+'/src/main/java/'+outer+'.java';assert not any(v in source for v in ['RootFailedStart','SnapshotKeyCloseWitness','pg9892','private'])
        java=(R/source).read_text();package,simple=outer.replace('/','.').rsplit('.',1);assert re.search(r'^package\s+'+re.escape(package)+r';',java,re.M);declaration=re.search(r'^public\s+(?:(?:final|sealed|abstract)\s+)?class\s+'+re.escape(simple)+r'\b',java,re.M);assert declaration
        proofs.append(dict(**{k:rows[0][k] for k in ['path','ruleId','startLine','endLine','inputSha256']},disposition='FALSE_POSITIVE_PROVEN_PUBLIC_CLASS_REFERENCE',proofKind=role,typedRole=typed_role,fullExactCaptureClosure=True,capturesProven=1,tokenCharacterSpan=[token_start,token_end],captureCharacterSpan=list(match.span(1)),declarationPath=source,declarationSourceSha256=sha(R/source),declarationLines=[java.count('\n',0,declaration.start())+1]))
    unresolved='evidence/01_PT/018_NK-OPS-001/1017_当sourceBootstrap20読取前提・scope仕様.md';rows=[x for x in pending if x['path']==unresolved and x['startLine']==x['endLine']==45];assert len(rows)==1 and sha(R/unresolved)==rows[0]['inputSha256']
    OUT.mkdir();(OUT/'updates.json').write_text(json.dumps(proofs,ensure_ascii=False,indent=2)+'\n');result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),originalMetadataSha256=sha(origin/'residual-metadata-shapes.json'),ruleManifestSha256=sha(rule),historicalScanSource=load(origin/'manifest.json')['historicalScanSource'],contentCommit=load(origin/'manifest.json')['contentCommit'],previousUnclassified=4484,additionalFalsePositives=2,remainingUnclassified=4482,retainedUnclassified=[dict(path=unresolved,line=45,reason='NO_COMPLETE_TYPED_SYMBOL_PROVENANCE; original role/source prerequisite not inferred')],updatesSha256=sha(OUT/'updates.json'),actualSecretCount=None,binaryClosed=0,binaryTotal=22,productTestsExecuted=0,scannerExecuted=False,targetsExecuted=False,operatorSourceReadSetExpanded=False,valuesOrValueHashesWritten=False,newAccepted=0,currentWholeG07Qualified=False,producer=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))))
    (OUT/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,classified=2,retainedCandidate=1,remaining=4482,manifestSha256=sha(OUT/'manifest.json'))))
if __name__=='__main__':main()
