"""Same frozen source six-module SpotBugs; test files excluded by normal source snapshot."""
from pathlib import Path
import json,hashlib,sys,xml.etree.ElementTree as E
import pg9666_pagination_static as runner
root=Path.cwd();runs=root.parent/'pgpt-runs/PG379';normal=runs/'pg21922-consumer-stop-six-main-compile-v1';slot=runs/'pg21924-consumer-stop-six-static-reactor-v1';assert not slot.exists();slot.mkdir();runner.SLOT=slot
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();m=json.loads((normal/'manifest.safe.json').read_text());assert m['actualExit']==0 and m['source']==sys.argv[1];assert all(sha(root/n)==h for n,h in m['begin']['inputHashes'].items())
command=m['begin']['command']+['com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check'];terminal=runner.step('spotbugs-reactor',command,normal/'snapshot',timeout=300);reports={}
for role in m['jars']:
 path=normal/'snapshot'/f'src/schubert-nk-{role}/target/spotbugsXml.xml'
 if path.exists():
  tree=E.parse(path).getroot();reports[role]=dict(path=str(path),sha256=sha(path),bugs=len(tree.findall('.//BugInstance')),missing=len(tree.findall('.//MissingClass')),errors=len(tree.findall('.//Error')))
value=dict(source=m['source'],actualExit=terminal['actualExit'],terminal=terminal,reports=reports,normalCompileManifestSha256=sha(normal/'manifest.safe.json'),jarsStillEqualCompile=all(sha(j['path'])==j['sha256'] for j in m['jars'].values()),sourceInputsUnchanged=all(sha(root/n)==h for n,h in m['begin']['inputHashes'].items()),suppressionsAdded=False,rulesUnchanged=True,productTestsExecuted=0,whole451Accepted=False,producerSha256=sha(__file__))
(slot/'manifest.safe.json').write_text(json.dumps(value,indent=2)+'\n');print(json.dumps(dict(actualExit=value['actualExit'],reports={k:[v['bugs'],v['missing'],v['errors']] for k,v in reports.items()},manifestSha256=sha(slot/'manifest.safe.json'))));assert len(reports)==6 and value['jarsStillEqualCompile'] and value['sourceInputsUnchanged'];sys.exit(terminal['actualExit'])
