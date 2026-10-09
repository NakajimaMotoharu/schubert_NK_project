"""Combined diagnostics only: same main bytes/test-only delta, NOT same full-source formal gate."""
import ast,json,hashlib,zipfile,xml.etree.ElementTree as ET
from pathlib import Path
from pg908_current_gap import code as previous
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379');R=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def class_bytes(p):
 with zipfile.ZipFile(p)as z:return {n:hashlib.sha256(z.read(n)).hexdigest()for n in z.namelist()if n.endswith('.class')}
def qualify():
 selected=W/'pg911-snapshot-selected-v3';record=json.loads((selected/'run.safe.json').read_bytes());assert record['actualExit']==0 and record['installedVmSource']=='e01612fcd7f2752df5ae0836b78538fd5e87f120'
 batch=selected/'batch';total=0;names=[]
 for p in batch.glob('TEST-*.xml'):
  r=ET.parse(p).getroot();assert all(int(r.get(k,'0'))==0 for k in ('failures','errors','skipped'));total+=int(r.get('tests','0'));names.append(p.name)
 assert total==44 and len(names)==5
 static=ET.parse(batch/'spotbugsXml.xml').getroot();assert not static.findall('.//BugInstance')
 old=W/'pg857-completed-reference-six-host-v1/batch/schubert-nk-batch-0.1.0-SNAPSHOT.jar';new=batch/old.name;assert class_bytes(old)==class_bytes(new)
 for name,hash_value in record['files'].items():assert sha(selected/name)==hash_value
 return record,batch/'jacoco.exec'
def code(extra):
 raw=previous().replace('pg908-current-native-gap-v1','pg914-snapshot-diagnostic-v1')
 marker='    assert len(data)==26';assert raw.count(marker)==1
 raw=raw.replace(marker,marker+"\n    extra=pathlib.Path("+repr(str(extra))+');assert sha(extra)=='+repr(sha(extra))+";data.append(extra)\n    assert len(data)==27")
 old="assert all(counts[k] == record['moduleCounters'][module][k]['missed'] for k in ('LINE', 'METHOD', 'CLASS', 'BRANCH'))";assert raw.count(old)==1
 raw=raw.replace(old,"assert all(counts[k] <= record['moduleCounters'][module][k]['missed'] for k in ('LINE','METHOD','CLASS','BRANCH'))")
 raw=raw.replace("'sourceOrClassExclusions':False}","'sourceOrClassExclusions':False,'diagnosticOnlyDifferentTestSources':True,'extraSelectedSha256':"+repr(sha(extra))+",'formalFullSourceGate':False}")
 ast.parse(raw);return raw
if __name__=='__main__':
 record,extra=qualify();env={'__file__':str(R/'pg914_snapshot_diagnostic.py'),'__name__':'different_test_sources_diagnostic'};exec(compile(code(extra),'<914 same main byte diagnostic only>','exec'),env);env['main']()
 p=W/'pg914-snapshot-diagnostic-v1/batch.xml';root=ET.parse(p).getroot();c=next(c for c in root.findall('package/class')if c.get('name').endswith('/InspectorUnitSnapshot'))
 print(json.dumps({'selectedTests':44,'selectedSource':record['source'],'mainClassByteMismatch':0,'snapshotCounters':{v.get('type'):{'missed':int(v.get('missed')),'covered':int(v.get('covered'))}for v in c.findall('counter')},'formalAccepted':False,'differentTestSourcesDiagnosticOnly':True}))
