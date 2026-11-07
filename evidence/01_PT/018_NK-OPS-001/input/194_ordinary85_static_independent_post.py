"""Independently bind ordinary85 source set, raw XML347, engine terminals and no mutation."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
import xml.etree.ElementTree as E
R=Path(__file__).resolve().parents[4]
P=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22382-ordinary85-test-static-v1'
OUT=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22384-ordinary85-test-static-independent-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
def main():
    assert not OUT.exists();m=load(P/'manifest.json');b=m['begin'];assert m['actualExit']==0 and m['checkedFiles']==85 and m['productTestsExecuted']==0 and m['sourceBytesUnchanged'] and not m['wholeF03Accepted']
    assert b==load(P/'begin.json');old=R/b['legacyAllowlistManifest']['path'];assert sha(old)==b['legacyAllowlistManifest']['sha256']=='5a5b61a9975861232c92a4af0759484e5d4fdccb083cc202a7fa7ad9d552b52a';assert set(b['inputHashes'])==set(load(old)['begin']['inputHashes'])
    assert m['source']==b['source']=='eed75aec2f60fc61a7534d55e852957804bb9b68' and b['productionCoreMain']=='7aed8eace7c844c2f79f2e39db766faf914890d5'
    blocked={'RootFailedStartRecoveryTest.java','RootFailedStartPairRecoveryTest.java','SnapshotKeyCloseWitness.java','pg9892_snapshot_key_close_witness.py'}
    for name,h in b['inputHashes'].items():
        assert not blocked.intersection(Path(name).parts) and '/src/test/java/' in name and name.startswith('src/') and name.endswith('.java')
        assert sha(R/name)==h==hashlib.sha256(subprocess.check_output(['git','show',m['source']+':'+name],cwd=R)).hexdigest()
    for name,h in {**b['toolHashes'],**b['dependencies']}.items():assert sha(name)==h
    for name,h in m['files'].items():assert sha(P/name)==h
    assert sha(R/b['driver']['path'])==b['driver']['sha256']
    actual=[]
    for tool,tag in [('pmd','violation'),('checkstyle','error')]:
        stage=m['stages'][tool];assert stage==load(P/(tool+'-exit.safe.json')) and not stage['timedOut']
        for stream in ['stdout','stderr']:assert sha(P/(tool+'.'+stream))==stage[stream+'Sha256']
        cmd=stage['command'];assert '/jdk-25.0.4/bin/java' in cmd[0]
        assert not any(x in cmd for x in ['--scan-classpath','execute','--select-class','--replace'])
        xml=P/(tool+'.xml');assert sha(xml)==m['reports'][tool]['sha256'];root=E.parse(xml).getroot();assert not any(x.tag.rsplit('}',1)[-1] in ['error','configerror'] for x in root if tool=='pmd');count=0
        for file in root:
            path=str(Path(file.get('name')).relative_to(R));assert path in b['inputHashes']
            for node in file:
                if node.tag.rsplit('}',1)[-1]!=tag:continue
                count+=1;actual.append(dict(tool=tool,path=path,sourceSha256=b['inputHashes'][path],ordinal=count,attributes=dict(node.attrib),message=' '.join(''.join(node.itertext()).split()),classification='UNCLASSIFIED'))
        assert count==m['reports'][tool]['raw']
    assert actual==load(P/'unclassified-sites.json') and len(actual)==m['unclassifiedSites']==347
    assert m['stages']['pmd']['actualExit']==4 and m['reports']['pmd']['raw']==347 and m['stages']['checkstyle']['actualExit']==m['reports']['checkstyle']['raw']==0
    assert all(x['classification']=='UNCLASSIFIED' for x in actual)
    OUT.mkdir();result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],productionCoreMain=b['productionCoreMain'],originalManifest=dict(path=str((P/'manifest.json').relative_to(R)),sha256=sha(P/'manifest.json')),inputHashes=b['inputHashes'],checkedFiles=85,pmdRaw=347,checkstyleRaw=0,unclassifiedSites=347,sourceBytesUnchanged=True,productTestsExecuted=0,newProductTests=0,newSourceProofs=0,newAcceptance=0,wholeF03Accepted=False,whole451Accepted=False,effortRate=None,verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__),source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()))
    (OUT/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,files=85,pmdRaw=347,checkstyleRaw=0,manifestSha256=sha(OUT/'manifest.json'))))
if __name__=='__main__':main()
