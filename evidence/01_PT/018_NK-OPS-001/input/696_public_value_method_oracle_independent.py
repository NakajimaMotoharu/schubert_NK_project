"""Independent raw-case/schema/selected-method/source evidence join, no original producer replay."""
from pathlib import Path
import datetime,hashlib,json,re,copy,subprocess
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';O=B/'evidence/PG24306-public-value-eighteen-oracle-independent-v1';assert not O.exists();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_bytes());P=B/'evidence/PG24304-public-value-eighteen-method-oracle-v1';m=load(P/'manifest.json');assert sha(P/'manifest.json')=='ba02a44c2b8041752c27d195c999cb6321a29e274134a344a9203acbb19ebfef' and m['actualExit']==0
cfg=load(R/m['config']['path']);assert sha(R/m['config']['path'])==m['config']['sha256'];relations=load(P/'method-oracle-relations.json');reviews=load(P/'case-oracle-reviews.json');old=load(B/'evidence/PG24190-public-value-six-source-byte-bridge-v1/historical-cases.json');classes={v['caseRef'].split('#')[0] for v in cfg['oracles']};assert len(classes)==4

def raw_cases(rows):
 assert len(rows)==18
 result=set()
 for r in rows:
  assert set(r)=={'classname','name','nonPass','result'} and r['classname'] in classes
  assert r['result']=='PASS' and type(r['nonPass']) is list and len(r['nonPass'])==0
  assert isinstance(r['name'],str) and re.fullmatch('[A-Za-z_$][A-Za-z0-9_$]*',r['name'])
  identity=r['classname']+'#'+r['name']+'()';assert identity not in result;result.add(identity)
 return result
expected=raw_cases(old);assert expected=={r['caseRef'] for r in reviews}=={r['caseRef'] for r in cfg['oracles']}
assert len(relations)==18 and {(v['className'],v['method'],v['descriptor']) for v in relations}=={(v['className'],v['name'],v['descriptor']) for v in load(B/'evidence/PG24296-public-value-six-official-filter-analysis-v1/official-retained-methods.json')}
ids={r['testId']:r for r in cfg['oracles']};assert len(ids)==18
for r in relations:
 assert r['testIds'] and all(t in ids for t in r['testIds']);assert set(r['caseRefs'])=={ids[t]['caseRef'] for t in r['testIds']}
 assert r['exactAllMethodCasesOrOracleComplete'] is False and sha(R/r['mainPath'])==r['sourceSha256']
 for t in r['testIds']:
  row=ids[t];text=(R/row['testPath']).read_text();marker='void '+row['method']+'(';start=text.index(marker);end=text.find('\n  @Test',start);body=text[start:end if end!=-1 else None]
  assert all(s in body for s in row['assertionTokens']) and row['expectationProductionGenerated'] is False
 for special in ['<clinit>','invalid','string','lambda$normalize$0']:
  if r['method']==special:assert r['invocationRelation'].startswith('INDIRECT_')
ident=load(B/'evidence/PG24190-public-value-six-source-byte-bridge-v1/test-source-git-identity.json');assert len(ident)==4
for r in ident:
 assert r['testSourceIdentical'] and r['historicalGitBlob']==r['currentGitBlob']==subprocess.check_output(['git','rev-parse','HEAD:'+r['path']],text=True).strip()
for path,pin in cfg['inputHashes'].items():assert sha(R/path)==pin
negative=[]
for label,mutate in [('method-suffix-mixed',lambda r:r[0].update(name=r[0]['name']+'()')),('unknown-display-name',lambda r:r[0].update(name='display name [1]')),('missing-field',lambda r:r[0].pop('name')),('unknown-field',lambda r:r[0].update(caseRef='UNKNOWN')),('failed-case',lambda r:r[0].update(result='FAIL')),('nonpass-case',lambda r:r[0].update(nonPass=['failure'])),('wrong-nonpass-type',lambda r:r[0].update(nonPass=())),('unknown-class',lambda r:r[0].update(classname='UNKNOWN')),('duplicate-case',lambda r:r.__setitem__(1,copy.deepcopy(r[0]))),('missing-case',lambda r:r.pop())]:
 a=copy.deepcopy(old);mutate(a)
 try:raw_cases(a)
 except (AssertionError,KeyError):negative.append(label)
 else:raise AssertionError(label)
# Existing bridge roles intentionally keep raw names; no suffix conversion needed there.
for filename in ['665_public_value_six_source_bridge.py','666_public_value_six_source_bridge_independent.py']:
 text=(B/'input'/filename).read_text();assert 'historical-cases.json' in text
assert m['explicitlyRelatedMethods']==m['originalSuccessfulCaseRefs']==18 and m['assertionSnippetChecks']==87
assert not m['currentRunQualified'] and not m['exactAllMethodCasesOrOracleComplete'] and not m['compilerOrJvmExecuted']
O.mkdir();v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),sourcePrograms=6,explicitlyRelatedMethods=18,originalCaseRefs=18,originalWholeTestClasses=4,assertionSnippetChecks=87,sourcePinsChecked=10,originalFourTestGitObjectsUnchanged=True,strictRawCaseSchemaCanonicalizedWithoutOriginalRewrite=True,rawCaseSchemaNegativeChecks=negative,ykt2259TargetsDisposition=dict(producer695='fixed canonical references only; original raw18 retained',independent696='separate strictschema/rawnegative10 passed',old665666='nonapplicable: original raw name preservation role, no signature join'),exactAllMethodCasesOrOracleComplete=False,wholeDependencyAccepted=False,currentRunQualified=False,original18Reexecuted=False,productTestsExecuted=0,newUniqueTests=0,newAcceptance=0,formalUpdated=False,effortRate=None,limitations=cfg['limitations'],reviewManifest=dict(path=str((P/'manifest.json').relative_to(R)),sha256=sha(P/'manifest.json')),config=m['config'],bugs=['BUG-2525'],ykts=['YKT-2259'],toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,methods=18,cases=18,assertions=87,schemaNegativeChecks=len(negative),manifestSha256=sha(O/'manifest.json'))))
