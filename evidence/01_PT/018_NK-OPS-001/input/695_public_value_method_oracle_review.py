"""Explicit historical method/assertion joins; never treats snippet review as full branch oracle."""
from pathlib import Path
import datetime,hashlib,json,re,copy
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';C=B/'input/694_public_value_eighteen_oracle_scope.json';O=B/'evidence/PG24304-public-value-eighteen-method-oracle-v1';assert not O.exists();load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();cfg=load(C)
proof=load(R/cfg['originalPost']);assert proof['actualExit']==0 and (proof['tests'],proof['suites'],proof['failures'],proof['errors'],proof['skipped'])==(18,4,0,0,0)
filt=load(R/cfg['filterProof']);assert filt['actualExit']==0 and filt['officialRetainedCodeMethods']==18 and filt['individuallyClassifiedStandardFilters']==12
bridge=B/'evidence/PG24190-public-value-six-source-byte-bridge-v1';identities=load(bridge/'test-source-git-identity.json');case_source=load(bridge/'historical-cases.json');print('case shape',type(case_source).__name__)
# Use the already verified public original case mapping, not a new run or an inferred count.
assert all(set(v)=={'classname','name','nonPass','result'} and v['result']=='PASS' and v['nonPass']==[] and re.fullmatch('[A-Za-z_$][A-Za-z0-9_$]*',v['name']) for v in case_source)
original_cases={v['classname']+'#'+v['name']+'()' for v in case_source}
assert len(original_cases)==len(case_source)==18

def validate(c):
 for path,pin in c['inputHashes'].items():assert sha(R/path)==pin
 assert len(c['oracles'])==18 and len({r['testId'] for r in c['oracles']})==18
 assert {r['caseRef'] for r in c['oracles']}==original_cases
 official=load(B/'evidence/PG24296-public-value-six-official-filter-analysis-v1/official-retained-methods.json')
 assert len(c['methods'])==18 and {(v['className'],v['method'],v['descriptor']) for v in c['methods']}=={(v['className'],v['name'],v['descriptor']) for v in official}
 ids={v['testId']:v for v in c['oracles']};assertions=[]
 for row in c['oracles']:
  assert row['expected'] and row['expectationProductionGenerated'] is False and row['assertionTokens']
  text=(R/row['testPath']).read_text();marker='void '+row['method']+'(';assert text.count(marker)==1;start=text.index(marker);end=text.find('\n  @Test',start);body=text[start:end] if end>=0 else text[start:]
  assert all(t in body for t in row['assertionTokens']),row['caseRef'];assertions.append(dict(caseRef=row['caseRef'],testId=row['testId'],declarationLine=text[:start].count('\n')+1,assertionSnippetCount=len(row['assertionTokens']),independentExpected=row['expected']))
 for row in c['methods']:
  assert set(row['testIds'])<=set(ids) and row['testIds'] and row['exactAllMethodCasesOrOracleComplete'] is False
  assert {ids[x]['caseRef'] for x in row['testIds']}==set(row['caseRefs'])
  assert sha(R/row['mainPath'])==row['sourceSha256']
 return assertions
reviews=validate(cfg)
# Mathematical expected values are reconstructed from the independent SS331 literal alphabet,
# never from production ALPHABET/generate. This only validates the Test's literal vectors.
test=next(p for p in cfg['inputHashes'] if p.endswith('/QuestionReceiptIdTest.java'));text=(R/test).read_text();alphabet='0123456789ABCDEFGHJKMNPQRSTVWXYZ';assert len(alphabet)==len(set(alphabet))==32
forward=''.join(alphabet[i] for i in range(26));reverse=''.join(alphabet[i] for i in range(31,5,-1))
assert 'FORWARD = "'+forward+'";' in text and 'REVERSE = "'+reverse+'";' in text
part=text.split('List<String> literalCycles =',1)[1].split('Map<String, Integer> expected',1)[0];literals=re.findall(r'"([0-9A-Z]+)"',part)
assert literals==[''.join(alphabet[(i*26+j)%32] for j in range(26)) for i in range(16)] and 64*26==1664 and 64//16==4
negative=[]
for label,mutate in [('missing-method',lambda c:c['methods'].pop()),('missing-case',lambda c:c['oracles'].pop()),('wrong-descriptor',lambda c:c['methods'][0].update(descriptor='BAD')),('wrong-case',lambda c:c['oracles'][0].update(caseRef='UNKNOWN#absent()')),('unknown-testid',lambda c:c['methods'][0]['testIds'].append('PT-ABSENT')),('missing-assert',lambda c:c['oracles'][0]['assertionTokens'].append('assertEquals(MISSING_EXPECTED, actual);')),('production-expected',lambda c:c['oracles'][0].update(expectationProductionGenerated=True)),('missing-expected',lambda c:c['oracles'][0].update(expected='')),('wrong-source-pin',lambda c:c['methods'][0].update(sourceSha256='0'*64))]:
 altered=copy.deepcopy(cfg);mutate(altered)
 try:validate(altered)
 except (AssertionError,KeyError):negative.append(label)
 else:raise AssertionError('negative accepted: '+label)
O.mkdir();(O/'method-oracle-relations.json').write_text(json.dumps(cfg['methods'],ensure_ascii=False,indent=2)+'\n');(O/'case-oracle-reviews.json').write_text(json.dumps(reviews,ensure_ascii=False,indent=2)+'\n')
v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),sourceProductionMain=cfg['productionMain'],sourcePrograms=6,explicitlyRelatedMethods=18,originalSuccessfulCaseRefs=18,originalWholeTestClasses=4,assertionSnippetChecks=sum(v['assertionSnippetCount'] for v in reviews),independentAlphabetVectorCounts=dict(alphabet=32,length=26,forwardReverse=2,concurrentLiteralCycles=16,drawsPer64Calls=1664,countsPerCycle=4),indirectClinitPrivateLambdaRelationsExplicit=True,standardFiltersAlreadyBound=12,exactAllMethodCasesOrOracleComplete=False,wholeDependencyAccepted=False,historical18Repeated=False,currentRunQualified=False,compilerOrJvmExecuted=False,productTestsExecuted=0,newUniqueTests=0,newAcceptance=0,formalUpdated=False,effortRate=None,limitations=cfg['limitations'],negativeChecks=negative,config=dict(path=str(C.relative_to(R)),sha256=sha(C)),files={p.name:sha(p) for p in O.iterdir()},toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,methods18=18,caseRefs18=18,assertions=v['assertionSnippetChecks'],negativeChecks=len(negative),manifestSha256=sha(O/'manifest.json'))))
