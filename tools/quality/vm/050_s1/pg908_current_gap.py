"""Offline current20/host6 exact coordinates; no old source/VM operation or exclusion."""
import ast,json
from pathlib import Path
R=Path(__file__).resolve().parent
STREAMS='''
    sixteen=W/'pg892-current-sixteen-native-v1';v16=json.loads((sixteen/'manifest.safe.json').read_bytes())
    eighteen=W/'pg903-current-eighteen-native-v1';v18=json.loads((eighteen/'manifest.safe.json').read_bytes())
    assert sha(eighteen/'manifest.safe.json')==record['previousEighteenManifestSha256']and sha(sixteen/'manifest.safe.json')==v18['previousSixteenManifestSha256']
    for name,digest in v16['qualifiedCohortManifestHashes'].items():
        q=W/name;assert sha(q/'manifest.safe.json')==digest;meta=json.loads((q/'manifest.safe.json').read_bytes());assert meta['actualExit']==0 and meta['productionSource']==record['productionSource']
        for i,v in enumerate(meta['selected']):
            p=q/(str(i)+'.exec');assert sha(p)==v['sha256'];data.append(p)
    for i,digest in enumerate(v18['bootstrapNativeHashes']):
        p=eighteen/('bootstrap-'+str(i)+'.exec');assert sha(p)==digest;data.append(p)
    for i,digest in enumerate(record['inspectorNativeHashes']):
        p=cohort/('inspector-'+str(i)+'.exec');assert sha(p)==digest;data.append(p)
    assert len(data)==26
'''
def code():
 raw=(R/'pg615_current_native_gap.py').read_text()
 for old,new in [('pg614-current-eight-native-v1','pg907-current-twenty-native-v1'),('4c178d8e6d2f76f097a315226586bb934041ce1805a5cd79811e2034b3b442c1','250d575bcd57a6eb52401c6abe5f274b53e30b39240f009b14f1d89a540866d5'),('23b14a44b10504172e030bbd6625926bf049fb5c','e01612fcd7f2752df5ae0836b78538fd5e87f120'),('pg615-current-native-gap-v1','pg908-current-native-gap-v1'),('pg599-candidate-bootstrap-six-host-v1','pg857-completed-reference-six-host-v1'),("record['hostExecHashes'][m]","host_record['moduleResults'][m]['execSha256']")]:
  assert old in raw,old;raw=raw.replace(old,new)
 start=raw.index("    for i, expected in enumerate(record['selected']):");end=raw.index('    gaps =',start)
 raw=raw[:start]+STREAMS+raw[end:];ast.parse(raw);return raw
if __name__=='__main__':
 env={'__file__':str(R/'pg908_current_gap.py'),'__name__':'current20_gap'};exec(compile(code(),'<908 qualified current20 XML>','exec'),env);env['main']()
