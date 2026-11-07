"""Individual JUnit thread-rule scope; no claim about lifecycle correctness and no Product execution."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import subprocess
import zipfile
R=Path(__file__).resolve().parents[4];RUNS=R.parent/'pgpt-runs/PG379'
BASE=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22382-ordinary85-test-static-v1';OUT=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22408-ordinary-thread158-scope-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
HELD={'RootFailedStartRecoveryTest.java','RootFailedStartPairRecoveryTest.java','SnapshotKeyCloseWitness.java','pg9892_snapshot_key_close_witness.py'}
def assess(text,row,main_names):
    path=row['path'];a=row['attributes'];parts=Path(path).parts
    if not path.startswith('src/') or '/src/test/java/' not in path or HELD.intersection(parts):return None
    if a['rule']!='DoNotUseThreads' or 'import org.junit.jupiter.api.Test;' not in text:return None
    pkg=re.search(r'^package ([\w.]+);$',text,re.M);owner=Path(path).stem
    if not pkg or pkg[1]!=a['package'] or a['class'].split('.')[0]!=owner or not re.search(r'\bclass\s+'+re.escape(owner)+r'\b',text):return None
    binary=pkg[1].replace('.','/')+'/'+owner
    if any(x==binary+'.class' or x.startswith(binary+'$') for x in main_names):return None
    lines=text.splitlines();start=int(a['beginline']);end=int(a['endline'])
    if not 0<start<=end<=len(lines) or not a.get('method'):return None
    if not re.search(r'\b'+re.escape(a['method'])+r'\s*\(',text):return None
    span='\n'.join(lines[start-1:end]);return dict(classification='NOT_APPLICABLE',reason='This exact finding is in a standalone JUnit Test/helper method, outside all six normal Production artifacts. The J2EE application-thread prohibition is inapplicable at this Test site. Thread ownership, bounded completion, resource cleanup and assertions are separate responsibilities and are not accepted by this classification.',testBinaryName=binary,enclosingMethod=a['method'],sourceSpanSha256=hashlib.sha256(span.encode()).hexdigest(),beginLine=start,endLine=end,ownershipQualified=False)
def negative_vectors():
    text='package p;\nimport org.junit.jupiter.api.Test;\nclass ExampleTest { void check(){ Thread.currentThread().interrupt(); }}'
    row=dict(path='src/a/src/test/java/p/ExampleTest.java',attributes=dict(rule='DoNotUseThreads',package='p',class_='ExampleTest',method='check',beginline='3',endline='3'));row['attributes']['class']=row['attributes'].pop('class_');assert assess(text,row,set())
    variants=[]
    for key,value in [('package','other'),('class','OtherTest'),('method','missing'),('beginline','0'),('endline','99')]:
        x=json.loads(json.dumps(row));x['attributes'][key]=value;variants.append((text,x,set()))
    x=json.loads(json.dumps(row));x['path']=x['path'].replace('/test/','/main/');variants.append((text,x,set()));variants.append((text,row,{'p/ExampleTest.class'}));variants.append((text.replace('import org.junit.jupiter.api.Test;',''),row,set()));assert all(assess(*v) is None for v in variants);return len(variants)
def main():
    assert not OUT.exists();mp=BASE/'manifest.json';assert sha(mp)=='e4eea946c71b78db2cca778259ef366cd4cd60c208708941a61067f48cee25a2';m=load(mp);rows=load(BASE/'unclassified-sites.json');selected=[x for x in rows if x['attributes']['rule']=='DoNotUseThreads'];assert len(rows)==347 and len(selected)==158
    nm=RUNS/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json';assert sha(nm)=='b2f07209804d71ee2ffbc4d9aca5311d4e6cf15721c74bcde411f86538cf4f27';normal=load(nm);names=set();jars={}
    for module,v in normal['jars'].items():
        assert sha(v['path'])==v['sha256'];jars[module]=v
        with zipfile.ZipFile(v['path']) as jar:names.update(jar.namelist())
    sites=[];inputs={}
    for row in selected:
        path=row['path'];assert not HELD.intersection(Path(path).parts);assert sha(R/path)==row['sourceSha256']==m['begin']['inputHashes'][path];inputs[path]=sha(R/path);a=assess((R/path).read_text(),row,names);sites.append(dict(original=row,assessment=a,status='CLASSIFIED_INDIVIDUALLY' if a else 'UNCLASSIFIED_SCOPE_UNPROVEN'))
    count=sum(x['assessment'] is not None for x in sites);assert len(inputs)==53;OUT.mkdir();(OUT/'site-classifications.json').write_text(json.dumps(sites,ensure_ascii=False,indent=2)+'\n');v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),productionCoreMain=normal['source'],originalManifest=dict(path=str(mp.relative_to(R)),sha256=sha(mp)),normalManifest=dict(path=str(nm),sha256=sha(nm)),normalJars=jars,inputHashes=inputs,targetSites=158,newIndividualClassifications=count,originalRawSites=347,priorIndividualClassifications=93,subsetUnclassifiedBefore=254,subsetUnclassifiedAfter=254-count,negativeMetadataVectors=negative_vectors(),productTestsExecuted=0,newProductTests=0,newSourceProofs=0,newAcceptance=0,threadOwnershipQualified=False,sourceBytesUnchanged=True,suppressionAdded=False,ruleConfigurationChanged=False,wholeF03Accepted=False,whole451Accepted=False,effortRate=None,files={'site-classifications.json':sha(OUT/'site-classifications.json')},producer=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__)))
    (OUT/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,classified=count,remaining=254-count,sourceFiles=53,manifestSha256=sha(OUT/'manifest.json'))))
if __name__=='__main__':main()
