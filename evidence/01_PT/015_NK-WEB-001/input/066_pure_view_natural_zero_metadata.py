"""Bind the one zero-branch Source to actual independent classinfo, without any product replay."""
from pathlib import Path
import datetime,hashlib,json,re,xml.etree.ElementTree as E
R=Path.cwd();B=R/'evidence/01_PT/015_NK-WEB-001';P=B/'evidence/PG24370-pure-view-seven-bounded-sixtyfour-independent-v1';O=B/'evidence/PG24378-pure-view-natural-zero-metadata-v1';assert not O.exists();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_bytes());m=load(P/'manifest.json');assert sha(P/'manifest.json')=='bb83280e8349a3049e2ce6956d01d6bbb2b59a3eae2945e73a8962a40b633ec5' and m['actualExit']==0
assert m['naturalZeroBranchSourceNames']==['TopBarViewModel.java'] and m['tests']==64
for name in ['classinfo.stdout','coverage.xml']:assert sha(P/name)==m['files'][name]
cfg=load(B/'input/062_pure_view_seven_scope.json');index=load(R/'evidence/01_PT/018_NK-OPS-001/evidence/PG23360-base59-named-proof-supplement-v1/current-normal-physical-index.json');target={n for n in cfg['currentMainPhysical'] if Path(index[n]['path']).name=='TopBarViewModel.java'};assert len(target)==1
rows=re.findall(r'^\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+class 0x([0-9a-f]{16}) (\S+)$',(P/'classinfo.stdout').read_text(),re.M);selected=[v for v in rows if v[6] in target];assert len(selected)==1
assert int(selected[0][1])==0 and selected[0][5]==index[selected[0][6]]['crc64']
tree=E.parse(P/'coverage.xml').getroot();sources=[v for v in tree.findall('.//sourcefile') if v.get('name')=='TopBarViewModel.java'];assert len(sources)==1 and all(c.get('type')!='BRANCH' for c in sources[0].findall('counter'))
assert m['individualSourceCounters']['TopBarViewModel.java']['BRANCH']['rate'] is None and m['strictNonemptyFour100GateExit']==1
O.mkdir();v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),originalIndependentPost=dict(path=str((P/'manifest.json').relative_to(R)),sha256=sha(P/'manifest.json')),source='TopBarViewModel.java',physicalClasses=1,exactCurrentCrc=selected[0][5],classinfoBranchTotal=0,xmlBranchCounterOmittedBecauseTotalZero=True,sourceBranchRate=None,branch100Inferred=False,strictNonemptySourceFour100GateExit=1,original64Reexecuted=False,productTestsExecuted=0,newAcceptance=0,formalUpdated=False,effortRate=None,toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,naturalZeroBound=True,manifestSha256=sha(O/'manifest.json'))))
