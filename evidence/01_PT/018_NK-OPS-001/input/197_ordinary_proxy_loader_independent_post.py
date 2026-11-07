"""Independent Java AST parse and metadata join; no Product/Test execution or type analysis."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
import pg9666_pagination_static as c
R=Path(__file__).resolve().parents[4];RUNS=R.parent/'pgpt-runs/PG379'
P=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22392-ordinary-proxy-loader93-v1'
BASE=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22382-ordinary85-test-static-v1'
OUT=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22394-ordinary-proxy-loader93-independent-v1';SLOT=RUNS/'pg22394-ordinary-proxy-loader93-independent-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
def main():
    assert not OUT.exists() and not SLOT.exists();m=load(P/'manifest.json');assert sha(P/'manifest.json')=='00c3bd27210de3f564494ce592aed761dbae8e9e0c77d79d3634ba694c207267' and m['actualExit']==0 and m['source']=='56f62c5487bea48dd77c73c975de346ce80b01a9';assert sha(BASE/'manifest.json')==m['originalManifest']['sha256'];rows=load(BASE/'unclassified-sites.json');sites=load(P/'site-classifications.json');assert sha(P/'site-classifications.json')==m['files']['site-classifications.json'];assert [x['original'] for x in sites]==[x for x in rows if x['attributes']['rule']=='UseProperClassLoader'] and len(rows)==347 and len(sites)==93
    for name,h in m['inputHashes'].items():
        assert not any(x in name for x in ['RootFailedStart','SnapshotKeyCloseWitness','pg9892_']) and '/src/test/java/' in name
        assert sha(R/name)==h==hashlib.sha256(subprocess.check_output(['git','show',m['source']+':'+name],cwd=R)).hexdigest()
    tool=R/'evidence/01_PT/018_NK-OPS-001/input/198_TestProxyLoaderAstCheck.java';head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip();assert hashlib.sha256(subprocess.check_output(['git','show',head+':'+str(tool.relative_to(R))],cwd=R)).hexdigest()==sha(tool)
    SLOT.mkdir();(SLOT/'classes').mkdir();c.SLOT=SLOT;jdk=R.parent/'toolchain/jdk-25.0.4/bin';stages={}
    stages['tool-javac']=c.step('tool-javac',[str(jdk/'javac'),'-proc:none','-encoding','UTF-8','-Xlint:all','-Werror','-d',str(SLOT/'classes'),str(tool)],R);assert stages['tool-javac']['actualExit']==0
    stages['parse']=c.step('parse',[str(jdk/'java'),'-cp',str(SLOT/'classes'),'TestProxyLoaderAstCheck',str(R),*sorted(m['inputHashes'])],R,timeout=120);assert stages['parse']['actualExit']==0 and not stages['parse']['timedOut']
    ast={}
    for line in (SLOT/'parse.stdout').read_text().splitlines():
        path,number,loader,iface,resolved,kind=line.split('\t');key=(path,int(number));assert key not in ast;ast[key]=dict(loaderExpression=loader,interfaceExpression=iface,resolvedInterface=resolved,profile=kind)
    selectedkeys=set()
    for x in sites:
        row=x['original'];key=(row['path'],int(row['attributes']['beginline']));selectedkeys.add(key);assert key in ast;assessment=x['assessment'];assert assessment and assessment['classification']=='NOT_APPLICABLE' and assessment['reason'];assert {k:assessment[k] for k in ast[key]}==ast[key] and ast[key]['profile']!='UNPROVEN'
    assert len(selectedkeys)==93 and len(ast)==93 and m['newIndividualClassifications']==93 and m['subsetUnclassifiedAfter']==254 and m['negativeMetadataVectors']==7
    # Independent AST counterexamples: rejected semantic assignments remain distinguishable.
    assert len([x for x in rows if x['attributes']['rule']!='UseProperClassLoader'])==254
    assert m['productTestsExecuted']==m['newProductTests']==m['newSourceProofs']==m['newAcceptance']==0 and not m['suppressionAdded'] and not m['ruleConfigurationChanged']
    OUT.mkdir();files={}
    for name in ['tool-javac.stdout','tool-javac.stderr','tool-javac-exit.safe.json','parse.stdout','parse.stderr','parse-exit.safe.json']:
        data=(SLOT/name).read_bytes();(OUT/name).write_bytes(data);files[name]=sha(OUT/name)
    result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],productionCoreMain=m['productionCoreMain'],originalClassificationManifest=dict(path=str((P/'manifest.json').relative_to(R)),sha256=sha(P/'manifest.json')),rawManifest=m['originalManifest'],targetSites=93,independentlyParsedAstSites=93,newIndividualClassifications=93,rawSitesRetained=347,subsetUnclassifiedAfter=254,productTestsExecuted=0,newProductTests=0,newSourceProofs=0,newAcceptance=0,sourceBytesUnchanged=True,ruleConfigurationChanged=False,suppressionAdded=False,wholeF03Accepted=False,whole451Accepted=False,effortRate=None,stages=stages,files=files,tool=dict(path=str(tool.relative_to(R)),sha256=sha(tool)),verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__),source=head))
    (OUT/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,astSites=93,classified=93,remaining=254,manifestSha256=sha(OUT/'manifest.json'))))
if __name__=='__main__':main()
