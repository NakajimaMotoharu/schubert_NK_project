from pathlib import Path
import sys,json,hashlib,os,xml.etree.ElementTree as E
import pg9666_pagination_static as r
root=Path.cwd();runs=root.parent/'pgpt-runs/PG379';comp=runs/'pg19412-qa054-protocol-six-main-compile-v1';m=json.loads((comp/'manifest.safe.json').read_text());assert m['source']=='da176a90e7d59c23aaa50b2a00f42c200590b775' and m['actualExit']==0
slot=runs/'pg19440-qa054-protocol-six-static-reactor-v1';assert not slot.exists();slot.mkdir();r.SLOT=slot;sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for p,h in m['begin']['inputHashes'].items():assert sha(root/p)==h
cmd=json.loads((runs/'pg19272-acceptor-parser-six-static-reactor-v1/manifest.safe.json').read_text())['terminal']['command'];terminal=r.step('spotbugs-six',cmd,comp/'snapshot',timeout=600);reports={}
for role,j in m['jars'].items():
 p=comp/'snapshot'/('src/schubert-nk-'+role+'/target/spotbugsXml.xml');n=E.parse(p).getroot();reports[role]={'bugs':len(list(n.iter('BugInstance'))),'errors':len(list(n.iter('Error'))),'missing':len(list(n.iter('MissingClass'))),'sha256':sha(p)}
result={'source':m['source'],'actualExit':terminal['actualExit'],'terminal':terminal,'reports':reports,'jarsStillEqualCompile':all(sha(j['path'])==j['sha256'] for j in m['jars'].values()),'sourceInputsUnchanged':all(sha(root/p)==h for p,h in m['begin']['inputHashes'].items()),'suppressionsAdded':False,'rulesUnchanged':True,'productTestsExecuted':0,'whole451Accepted':False};(slot/'manifest.safe.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'actualExit':terminal['actualExit'],'reports':reports,'jarsUnchanged':result['jarsStillEqualCompile']}));raise SystemExit(terminal['actualExit'])
