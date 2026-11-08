"""Reverse current canonical shape references and document-only correction, without Product execution."""
from pathlib import Path
import datetime, hashlib, json, subprocess, copy
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';S=B/'evidence/PG24744-current-component296-correction-v1';O=B/'evidence/PG24752-component296-correction-independent-v1';assert not O.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_bytes())
mp=S/'manifest.json';assert sha(mp)=='7ba7a65d0e63dc8157f35a0fb6803d8ecf196d7c006dbfe8929cb0e6ac0fbf0b';m=load(mp);assert m['actualExit']==0
sp=S/'named-shapes.json';assert sha(sp)==m['namedShapesSha256'];rows=load(sp);assert len(rows)==69 and len({r['type'] for r in rows})==69
for path,h in m['inputFixtures'].items():assert sha(R/path)==h
read=lambda n:[l.split('\t') for l in (R/'src/schubert-nk-protocol/src/test/resources/protocol'/n).read_text().splitlines() if l.strip() and not l.startswith('#')]
types=read('named-types-ss323.tsv');fields=read('fields-ui234-236.tsv');accessors=read('named-accessors-independent.tsv');binding=dict(accessors);by={r['type']:r for r in rows};checkedPairs=0
for layout,data,record in types:
 for area,typename in [('DATA',data),('RECORD',record)]:
  if typename=='-':continue
  source=[r for r in fields if r[0]==layout and r[1]==area and r[6]!='F'];expected=[dict(name=r[2],length=int(r[4]),wire=r[5],presence=r[6],getter=binding[r[2]]) for r in source]
  assert by[typename]['independentFields']==expected and dict(layout=layout,area=area) in by[typename]['layouts'];checkedPairs+=1
assert checkedPairs==78
actual=dict(currentNamedTypes=len(rows),currentCanonicalComponents=sum(len(r['independentFields']) for r in rows),currentOptionalComponents=sum(f['wire']=='X' and f['presence'] in ['C','O'] for r in rows for f in r['independentFields']),currentEmptyTypes=sum(not r['independentFields'] for r in rows),currentPublicBindings=len(binding))
assert actual==dict(currentNamedTypes=69,currentCanonicalComponents=296,currentOptionalComponents=79,currentEmptyTypes=4,currentPublicBindings=135)
for k,v in actual.items():assert type(m[k]) is int and m[k]==v
helper=R/m['helper']['path'];assert sha(helper)==m['helper']['sha256'] and hashlib.sha256(subprocess.check_output(['git','show',m['testSource']+':'+m['helper']['path']])).hexdigest()==sha(helper);assert 'assertEquals(296, components,' in helper.read_text()
for r in m['mandatorySupplementFor']:assert sha(R/r['path'])==r['sha256']
before=load(B/'evidence/PG24742-component-count-documentation-before-v1/manifest.json');changed=[]
for r in m['correctedActiveDocuments']:
 p=R/r['path'];old=subprocess.check_output(['git','show',before['head']+':'+r['path']]);assert hashlib.sha256(old).hexdigest()==r['beforeSha256'] and sha(p)==r['sha256'];text=p.read_text();prefix=old.decode().replace('295','296');assert text.startswith(prefix) and '必須補足' in text[len(prefix):] and r['replacedOldLiteralCount']==old.count(b'295');changed.append(r['replacedOldLiteralCount'])
assert sorted(changed)==[0,2]
def counts_contract(x):
 assert all(type(x[k]) is int and x[k]==v for k,v in actual.items())
checks=0
for field,value in [('currentCanonicalComponents',295),('currentCanonicalComponents',True),('currentNamedTypes',68),('currentOptionalComponents',78),('currentEmptyTypes',3),('currentPublicBindings',134)]:
 bad=copy.deepcopy(actual);bad[field]=value
 try:counts_contract(bad)
 except AssertionError:checks+=1
 else:raise AssertionError('old or malformed counts accepted')
assert m['newAcceptance']==m['productTestsExecuted']==m['newProductTests']==m['newJavaCompilerExecutions']==0 and m['formalUpdated'] is False and m['effortRate'] is None
O.mkdir();out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],testSource=m['testSource'],producerManifest=dict(path=str(mp.relative_to(R)),sha256=sha(mp)),currentNamedTypes=69,currentCanonicalComponents=296,currentOptionalComponents=79,currentEmptyTypes=4,currentPublicBindings=135,canonicalLayoutAreaPairs=checkedPairs,metadataNegativeChecks=checks,changedActiveDocuments=2,frozenReferencesPreserved=3,oldPostMethodCountsRemainValid=True,sourceRegistryAcceptedDelta=0,newAcceptance=0,newProductTests=0,productTestsExecuted=0,newJavaCompilerExecutions=0,newCoverageMeasurement=False,formalUpdated=False,effortRate=None,toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,components=296,types=69,layoutAreaPairs=checkedPairs,metadataNegativeChecks=checks,manifestSha256=sha(O/'manifest.json'))))
