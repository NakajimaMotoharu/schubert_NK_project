"""Independently check every Test method AST owner and absence in Production Main artifacts."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
import zipfile
import pg9666_pagination_static as c
R=Path(__file__).resolve().parents[4];RUNS=R.parent/'pgpt-runs/PG379'
P=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22408-ordinary-thread158-scope-v1'
BASE=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22382-ordinary85-test-static-v1'
OUT=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22410-ordinary-thread158-independent-v1';SLOT=RUNS/'pg22410-ordinary-thread158-independent-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
def contained(row,methods):
    a=row['attributes'];key=(row['path'],a['class'],a['method']);return any(start<=int(a['beginline'])<=int(a['endline'])<=end for start,end in methods.get(key,[]))
def main():
    assert not OUT.exists() and not SLOT.exists();m=load(P/'manifest.json');assert sha(P/'manifest.json')=='be92fb45f6222e260be325529431f70be217a4dc1cd7656b53f484b2dd052709' and m['actualExit']==0 and m['source']=='1608ad70186461ea6903bcf9783fc152f0b10520';assert sha(BASE/'manifest.json')==m['originalManifest']['sha256'];rows=load(BASE/'unclassified-sites.json');sites=load(P/'site-classifications.json');assert sha(P/'site-classifications.json')==m['files']['site-classifications.json'];assert [x['original'] for x in sites]==[x for x in rows if x['attributes']['rule']=='DoNotUseThreads'];assert len(rows)==347 and len(sites)==158 and len(m['inputHashes'])==53
    main_names=set()
    for v in m['normalJars'].values():
        assert sha(v['path'])==v['sha256']
        with zipfile.ZipFile(v['path']) as jar:main_names.update(jar.namelist())
    for name,h in m['inputHashes'].items():
        assert '/src/test/java/' in name and not any(x in name for x in ['RootFailedStart','SnapshotKeyCloseWitness','pg9892_']);assert sha(R/name)==h==hashlib.sha256(subprocess.check_output(['git','show',m['source']+':'+name],cwd=R)).hexdigest()
    tool=R/'evidence/01_PT/018_NK-OPS-001/input/201_TestMethodScopeAstCheck.java';head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip();assert hashlib.sha256(subprocess.check_output(['git','show',head+':'+str(tool.relative_to(R))],cwd=R)).hexdigest()==sha(tool)
    SLOT.mkdir();(SLOT/'classes').mkdir();(SLOT/'source').mkdir();mirror=SLOT/'source/TestMethodScopeAstCheck.java';mirror.write_bytes(tool.read_bytes());assert sha(mirror)==sha(tool);c.SLOT=SLOT;jdk=R.parent/'toolchain/jdk-25.0.4/bin';stages={}
    stages['tool-javac']=c.step('tool-javac',[str(jdk/'javac'),'-proc:none','-encoding','UTF-8','-Xlint:all','-Werror','-d',str(SLOT/'classes'),str(mirror)],R);assert stages['tool-javac']['actualExit']==0
    stages['parse']=c.step('parse',[str(jdk/'java'),'-cp',str(SLOT/'classes'),'TestMethodScopeAstCheck',str(R),*sorted(m['inputHashes'])],R,timeout=120);assert stages['parse']['actualExit']==0 and not stages['parse']['timedOut'];methods={}
    for line in (SLOT/'parse.stdout').read_text().splitlines():
        path,cl,method,start,end=line.split('\t');methods.setdefault((path,cl,method),[]).append((int(start),int(end)))
    for x in sites:
        row=x['original'];a=x['assessment'];assert a and a['classification']=='NOT_APPLICABLE' and a['reason'] and contained(row,methods);assert not a['ownershipQualified'];assert a['testBinaryName']==row['attributes']['package'].replace('.','/')+'/'+Path(row['path']).stem
        binary=a['testBinaryName'];assert not any(n==binary+'.class' or n.startswith(binary+'$') for n in main_names)
        lines=(R/row['path']).read_text().splitlines();span='\n'.join(lines[int(row['attributes']['beginline'])-1:int(row['attributes']['endline'])]);assert hashlib.sha256(span.encode()).hexdigest()==a['sourceSpanSha256']
    first=sites[0]['original'];negative=[]
    for k,v in [('method','missing_method'),('class','MissingClass'),('beginline','0'),('endline','999999')]:
        bad=json.loads(json.dumps(first));bad['attributes'][k]=v;negative.append(not contained(bad,methods))
    bad=json.loads(json.dumps(first));bad['path']='src/unknown/src/test/java/X.java';negative.append(not contained(bad,methods));assert all(negative)
    correction=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22404-coding-rule-reference-correction-v1/manifest.json';cm=load(correction);assert cm['actualExit']==0 and len(cm['rows'])==2 and sha(R/cm['canonical']['path'])==cm['canonical']['sha256']
    for row in cm['rows']:
        old=correction.parent/row['preservedOriginalFile'];new=R/row['path'];assert sha(old)==row['beforeSha256'] and sha(new)==row['afterSha256'] and new.read_bytes().startswith(old.read_bytes());assert '411_コーディング規約.md' in new.read_text()
    assert m['newIndividualClassifications']==158 and m['subsetUnclassifiedAfter']==96 and m['negativeMetadataVectors']==8 and not m['threadOwnershipQualified'] and not m['wholeF03Accepted'];OUT.mkdir();files={}
    for name in ['tool-javac.stdout','tool-javac.stderr','tool-javac-exit.safe.json','parse.stdout','parse.stderr','parse-exit.safe.json']:
        (OUT/name).write_bytes((SLOT/name).read_bytes());files[name]=sha(OUT/name)
    result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],productionCoreMain=m['productionCoreMain'],originalClassificationManifest=dict(path=str((P/'manifest.json').relative_to(R)),sha256=sha(P/'manifest.json')),rawManifest=m['originalManifest'],sourceFiles=53,targetSites=158,independentlyBoundMethodSites=158,newIndividualClassifications=158,originalRawSites=347,priorIndividualClassifications=93,subsetUnclassifiedBefore=254,subsetUnclassifiedAfter=96,independentNegativeMetadataVectors=len(negative),threadOwnershipQualified=False,productTestsExecuted=0,newProductTests=0,newSourceProofs=0,newAcceptance=0,sourceBytesUnchanged=True,ruleConfigurationChanged=False,suppressionAdded=False,wholeF03Accepted=False,whole451Accepted=False,effortRate=None,stages=stages,files=files,correctionManifest=dict(path=str(correction.relative_to(R)),sha256=sha(correction)),tool=dict(path=str(tool.relative_to(R)),sha256=sha(tool),mirrorSha256=sha(mirror)),verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__),source=head))
    (OUT/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,sites=158,remaining=96,manifestSha256=sha(OUT/'manifest.json'))))
if __name__=='__main__':main()
