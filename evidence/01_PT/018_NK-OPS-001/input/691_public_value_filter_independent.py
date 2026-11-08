"""Independent exact signature partition; no analyzer/JVM/product replay."""
from pathlib import Path
from collections import Counter
import datetime,hashlib,json,copy
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';O=B/'evidence/PG24298-public-value-six-method-filter-independent-v1';assert not O.exists();load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();P=B/'evidence/PG24296-public-value-six-official-filter-analysis-v1';m=load(P/'manifest.json');assert sha(P/'manifest.json')=='a4465f219c6615b09bc7ee802c81f3717059f7241c912e1a82d88e26d6dbc280' and m['actualExit']==0
bridge=B/'evidence/PG24190-public-value-six-source-byte-bridge-v1';rows=load(bridge/'source-byte-bridges.json');metadata=B/'evidence/PG23972-current-main-method-delta42-v1/class-method-inventory.json';raw={v['physicalKey']:v for v in load(metadata)};official=load(P/'official-retained-methods.json')
allowed={
 'AnswerResult':{('hashCode','()I'),('equals','(Ljava/lang/Object;)Z'),('body','()Ljava/lang/String;'),('answeredAt','()Ljava/time/Instant;')},
 'QuestionReceiptId':{('hashCode','()I'),('equals','(Ljava/lang/Object;)Z'),('value','()Ljava/lang/String;')},
 'QuestionReceiptIdGenerator':set(), 'StubAnswerProvider':set(),
 'RequestLogDetails':{('<init>','()V')},
 'InspectorSettings':{('hashCode','()I'),('equals','(Ljava/lang/Object;)Z'),('credentialRoot','()Ljava/nio/file/Path;'),('databaseUrl','()Ljava/lang/String;')},
}
rawsets={};filtered=[];sources={}
for r in rows:
 v=raw[r['physicalKey']];owner=r['physicalKey'][4:-6];name=owner.split('/')[-1]
 assert v['classSha256']==r['classSha256']==m['exactPhysicalMembers'][owner+'.class'] and v['sourceSha256']==r['sourceSha256']==sha(R/r['mainPath'])
 source=(R/r['mainPath']).read_text();sources[r['mainPath']]=r['sourceSha256'];pairs={(x['name'],x['descriptor']) for x in v['structure']['methods'] if x['hasCode']};rawsets[owner]=pairs
 assert allowed[name]<=pairs
 for method,desc in sorted(allowed[name]):
  info=next(x for x in v['structure']['methods'] if x['name']==method and x['descriptor']==desc)
  if name=='RequestLogDetails':
   assert info['flags']==2 and info['codeLength']==5 and 'private RequestLogDetails() {}' in source;reason='official private empty no-arg constructor filter; explicitly declared utility constructor, not unimplemented code'
  else:
   assert 'public record '+name+'(' in source
   if method in ['hashCode','equals']:
    assert info['flags']==17 and info['codeLength']==(7 if method=='hashCode' else 8) and (' '+method+'(') not in source;reason='official record generated ObjectMethods filter'
   else:
    assert info['flags']==1 and info['codeLength']==5 and (method+'()') not in source;reason='official record generated component accessor filter'
  filtered.append(dict(className=owner,name=method,descriptor=desc,sourcePath=r['mainPath'],sourceSha256=r['sourceSha256'],classSha256=r['classSha256'],codeLength=info['codeLength'],reason=reason,coverageManuallyExcluded=False))
assert len(filtered)==12

def validate(data):
 assert len(data)==18
 actual=set()
 for x in data:
  assert set(x)=={'className','name','descriptor','emptyDataMethodMissed','emptyDataInstructionsMissed'}
  assert type(x['emptyDataMethodMissed']) is int and x['emptyDataMethodMissed']==1
  assert type(x['emptyDataInstructionsMissed']) is int and x['emptyDataInstructionsMissed']>0
  key=(x['className'],x['name'],x['descriptor']);assert key not in actual;actual.add(key)
 expected={(owner,name,desc) for owner,pairs in rawsets.items() for name,desc in pairs-allowed[owner.split('/')[-1]]}
 assert actual==expected
 for r in rows:assert sum(x['className']==r['physicalKey'][4:-6] for x in data)==r['historicalMeasuredMethods']
 return True
assert validate(official)
negative=[]
for label,mutate in [
 ('missing-method',lambda x:x.pop()),('duplicate-method',lambda x:x.append(copy.deepcopy(x[0]))),
 ('wrong-descriptor',lambda x:x[0].update(descriptor='()V_BAD')),
 ('wrong-owner',lambda x:x[0].update(className='dev/codex/NotCurrentOwner')),
 ('wrong-name',lambda x:x[0].update(name='absentUserMethod')),
 ('method-bool',lambda x:x[0].update(emptyDataMethodMissed=True)),
 ('instruction-bool',lambda x:x[0].update(emptyDataInstructionsMissed=True)),
 ('empty-no-code-method',lambda x:x[0].update(emptyDataInstructionsMissed=0)),
 ('unexpected-field',lambda x:x[0].update(inferredCoverage100=True)),
 ('generated-getter-replaces-explicit',lambda x:next(r for r in x if r['name']=='fingerprintVersions').update(name='credentialRoot',descriptor='()Ljava/nio/file/Path;'))]:
 altered=copy.deepcopy(official);mutate(altered)
 try:validate(altered)
 except AssertionError:negative.append(label)
 else:raise AssertionError('negative was not rejected: '+label)
for k,pin in m['files'].items():assert sha(P/k)==pin
for stage in m['stages'].values():assert stage['actualExit']==0 and not stage['timedOut']
cp=m['stages']['analysis']['command'];assert '-cp' in cp;parts=cp[cp.index('-cp')+1].split(':');assert len(parts)==5 and not any('schubert-nk-' in Path(p).name for p in parts)
assert m['emptyExecutionData'] and m['allAnalyzedMethodsUncovered'] and m['productClassPathEntries']==0 and not m['productClassInitializationOrInvocation']
# Only the normal code-identity/filter partition is sealed; old18 oracle/callee/current-run stays separate.
O.mkdir();(O/'individual-standard-filter-methods.json').write_text(json.dumps(filtered,ensure_ascii=False,indent=2)+'\n')
value=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),sourceProductionMain='7aed8eace7c844c2f79f2e39db766faf914890d5',rawCodeMethods=30,officialRetainedCodeMethods=18,individuallyClassifiedStandardFilters=12,unknownFilterDifferences=0,reasonCounts=dict(Counter(v['reason'] for v in filtered)),explicitInspectorAccessorAndRedactedToStringsRetained=True,analyzerTargetDataAllUncovered=True,coverageMeasured=False,manualCoverageExclusions=[],historical18Reexecuted=False,historicalOracleOrCalleeIndependentlyQualified=False,currentRunQualified=False,wholeWbsAccepted=False,negativeChecks=negative,sourceHashes=sources,originalAnalysisManifest=dict(path=str((P/'manifest.json').relative_to(R)),sha256=sha(P/'manifest.json')),originalByteBridgeManifest=dict(path=str((bridge/'manifest.json').relative_to(R)),sha256=sha(bridge/'manifest.json')),files={p.name:sha(p) for p in O.iterdir()},toolSha256=sha(Path(__file__)),productTestsExecuted=0,newAcceptance=0,formalUpdated=False,effortRate=None)
(O/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,raw30Retained18Filtered12=True,unknown=0,negativeChecks=len(negative),manifestSha256=sha(O/'manifest.json'))))
