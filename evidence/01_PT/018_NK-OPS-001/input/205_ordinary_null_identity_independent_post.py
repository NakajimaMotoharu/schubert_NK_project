"""Reuse the qualified parse-only AST tool on the new fourteen-site source set, no Test execution."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
import pg9666_pagination_static as c
R=Path(__file__).resolve().parents[4];RUNS=R.parent/'pgpt-runs/PG379';P=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22418-null-identity14-sites-v1';OUT=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22420-null-identity14-independent-v1';SLOT=RUNS/'pg22420-null-identity14-independent-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
def main():
    assert not OUT.exists() and not SLOT.exists();m=load(P/'manifest.json');assert sha(P/'manifest.json')=='d5d8672750fbd6bb36764a9d770777cc1391735ac0160b382d221935d00b6f6e' and m['actualExit']==0 and m['source']=='7bcaa157f9aebe16b1d4fef5cc12ded01b754a5b';sites=load(P/'site-classifications.json');assert sha(P/'site-classifications.json')==m['files']['site-classifications.json'];base=R/m['originalManifest']['path'];assert sha(base)==m['originalManifest']['sha256'];rows=load(base.parent/'unclassified-sites.json');selected=[x for x in rows if x['attributes']['rule'] in ['NullAssignment','CompareObjectsWithEquals']];assert len(sites)==len(selected)==14 and sorted(x['original']['ordinal'] for x in sites)==sorted(x['ordinal'] for x in selected)
    for name,h in m['inputHashes'].items():
        assert '/src/test/java/' in name and not any(x in name for x in ['RootFailedStart','SnapshotKeyCloseWitness','pg9892_']);assert sha(R/name)==h==hashlib.sha256(subprocess.check_output(['git','show',m['source']+':'+name],cwd=R)).hexdigest()
    prior=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22410-ordinary-thread158-independent-v1/manifest.json';assert sha(prior)=='b7a9022920798dd9c82e80a3e5165fca4a19a82de4d700568c46382c86f929f4';old=load(prior);tool=R/old['tool']['path'];owned=RUNS/'pg22410-ordinary-thread158-independent-v1';assert sha(tool)==old['tool']['sha256']==sha(owned/'source/TestMethodScopeAstCheck.java')==old['tool']['mirrorSha256'];assert old['stages']['tool-javac']['actualExit']==0
    classes={p.name:sha(p) for p in (owned/'classes').glob('*.class')};assert set(classes)=={'TestMethodScopeAstCheck.class','TestMethodScopeAstCheck$1.class'}
    SLOT.mkdir();c.SLOT=SLOT;stage=c.step('parse',[str(R.parent/'toolchain/jdk-25.0.4/bin/java'),'-cp',str(owned/'classes'),'TestMethodScopeAstCheck',str(R),*sorted(m['inputHashes'])],R,timeout=120);assert stage['actualExit']==0 and not stage['timedOut'];methods={}
    for line in (SLOT/'parse.stdout').read_text().splitlines():
        path,cl,method,start,end=line.split('\t');methods.setdefault((path,cl,method),[]).append((int(start),int(end)))
    for s in sites:
        row=s['original'];assert row in selected and s['classification']=='NOT_APPLICABLE' and s['reason'] and not s['dynamicAssertionReexecuted'];a=row['attributes'];method=a['method'];method='<init>' if method==a['class'].split('.')[-1] else method;matches=[(lo,hi) for lo,hi in methods.get((row['path'],a['class'],method),[]) if lo<=int(a['beginline'])<=int(a['endline'])<=hi];assert len(matches)==1
        lo,hi=matches[0];lines=(R/row['path']).read_text().splitlines();number=int(a['beginline']);assert lines[number-1].strip()==s['expectedSourceLine'];assert s['localWitness'] in '\n'.join(lines[lo-1:hi]);window='\n'.join(lines[max(0,number-5):number+30]);assert hashlib.sha256(window.encode()).hexdigest()==s['localWindowSha256'];assert (a['rule']=='NullAssignment')==s['expectedSourceLine'].endswith('= null;')
        if a['rule']=='CompareObjectsWithEquals':assert s['expectedSourceLine']=='case "equals" -> proxy == args[0];' and s['localWitness']=='case "hashCode" -> System.identityHashCode(proxy);'
    assert m['subsetUnclassifiedBefore']==96 and m['subsetUnclassifiedAfter']==82 and m['newIndividualClassifications']==14 and not m['dynamicBehaviourQualified'] and not m['suppressionAdded'];assert classes=={p.name:sha(p) for p in (owned/'classes').glob('*.class')};OUT.mkdir();files={}
    for name in ['parse.stdout','parse.stderr','parse-exit.safe.json']:(OUT/name).write_bytes((SLOT/name).read_bytes());files[name]=sha(OUT/name)
    result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],productionCoreMain=m['productionCoreMain'],originalClassificationManifest=dict(path=str((P/'manifest.json').relative_to(R)),sha256=sha(P/'manifest.json')),targetSites=14,independentlyBoundMethodAndWitnessSites=14,newIndividualClassifications=14,originalRawSites=347,priorIndividualClassifications=251,subsetUnclassifiedBefore=96,subsetUnclassifiedAfter=82,productTestsExecuted=0,newProductTests=0,newSourceProofs=0,newAcceptance=0,dynamicBehaviourQualified=False,sourceBytesUnchanged=True,suppressionAdded=False,wholeF03Accepted=False,whole451Accepted=False,effortRate=None,stage=stage,files=files,reusedParseTool=dict(manifestPath=str(prior.relative_to(R)),manifestSha256=sha(prior),toolSourceSha256=sha(tool),toolPhysical=classes,noToolRecompile=True,noProductClasspath=True),verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__),source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()))
    (OUT/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,sites=14,remaining=82,manifestSha256=sha(OUT/'manifest.json'))))
if __name__=='__main__':main()
