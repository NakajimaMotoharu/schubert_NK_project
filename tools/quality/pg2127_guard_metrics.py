"""Read qualified same-source method counters; public subset proof, not global coverage acceptance."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from lan_server import run
from pg1446_current_cold_stage import W
from pg2124_metadata_boundary_full_six import production

SCOPE={
 'dev/codex/schubert/nk/batch/file/CaddyPublicConfiguration':['requireStableDirectory','requireDirectoryMetadata','requireInodeIdentity','requireNoAccessAcl'],
 'dev/codex/schubert/nk/batch/file/MorningBackupArtifacts':['requireDirectoryMetadata','requireFileMetadata','requireToolMetadata','requireNoAccessAcl'],
}

def main():
    os.umask(0o077)
    outer=json.loads((W/'pg2125-metadata-boundary-full-qualified-v1/manifest.safe.json').read_bytes())
    if outer['actualExit']!=0 or outer['result']['productionSource']!=production():raise ValueError('qualified same-source full required')
    v=outer['result'];code='INPUT='+repr({'source':v['productionSource'],'xml':v['qualificationInputs']['batch']['coverageXml'],'jar':v['jarHashes']['batch'],'scope':SCOPE})+'''
import hashlib,json,xml.etree.ElementTree as ET
from pathlib import Path
t=Path('/home/mini/schubert-nk-pgpt/source-full-PG2124/src/schubert-nk-batch/target')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if sha(t/'site/jacoco/jacoco.xml')!=INPUT['xml']or sha(t/'schubert-nk-batch-0.1.0-SNAPSHOT.jar')!=INPUT['jar']:raise ValueError('qualified XML and Main bytes required')
x=ET.parse(t/'site/jacoco/jacoco.xml').getroot();result={}
for name,methods in INPUT['scope'].items():
 cs=[c for c in x.findall('.//class')if c.attrib['name']==name]
 if len(cs)!=1:raise ValueError('one physical class scope required')
 result[name]={}
 for method in methods:
  ms=[m for m in cs[0].findall('method')if m.attrib['name']==method]
  if len(ms)!=1:raise ValueError('one physical method scope required')
  counters={c.attrib['type']:{k:int(c.attrib[k])for k in ['missed','covered']}for c in ms[0].findall('counter')if c.attrib['type']in ['LINE','METHOD','BRANCH']}
  if set(counters)!={'LINE','METHOD','BRANCH'}or any(c['missed']!=0 or c['covered']<=0 for c in counters.values()):raise ValueError('all method counters exact100 required')
  result[name][method]=counters
totals={k:sum(m[k]['covered']for c in result.values()for m in c.values())for k in ['LINE','METHOD','BRANCH']}
if totals!={'LINE':46,'METHOD':8,'BRANCH':68}:raise ValueError('independent bounded subset count mismatch')
print(json.dumps({'methods':result,'totals':totals,'classScopeNotFullyAccepted':True,'globalCoverage100':False,'formalAccepted':False}))
'''
    from pyflakes.api import check
    if check(code,'<actual qualified method metrics>'):raise ValueError('all metric exports required')
    out=W/'pg2127-guard-metrics-v1';out.mkdir(mode=0o700)
    status,output=run("python3 - <<'PG2127'\n"+code+'\nPG2127',timeout=30)
    (out/'observer.private.log').write_text(output)
    result={'actualExit':status,'source':production(),'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'payloadSha256':hashlib.sha256(code.encode()).hexdigest(),'fullQualificationSha256':hashlib.sha256((W/'pg2125-metadata-boundary-full-qualified-v1/manifest.safe.json').read_bytes()).hexdigest(),'wholeLeafAcceptedDelta':0,'formalAccepted':False,'vmActions0':True}
    if not status:result.update(json.loads(next(l for l in output.splitlines()if l.startswith('{'))))
    (out/'manifest.safe.json').write_text(json.dumps(result,sort_keys=True))
    print(json.dumps(result));return status

if __name__=='__main__':raise SystemExit(main())
