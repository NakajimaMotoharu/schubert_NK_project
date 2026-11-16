"""Join exact whole-source common-harness proof, class-complete static XML and fifteen site decisions."""
from pathlib import Path
import datetime
import hashlib
import json
import xml.etree.ElementTree as ET

r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
up=b/'evidence/PG37016-p020-whole124-independent-v1/manifest.json';u=load(up);sp=b/'evidence/PG37018-p020-five-main-static-v1/manifest.json';s=load(sp)
assert u['actualExit']==0 and u['success']==124 and s['actualUnitSource']==u['source'] and s['sourceCore']==u['sourceCore']
assert all(sha(r/path)==h for path,h in s['sourceHashes'].items()) and s['classHashes']==u['classSha256']
for name in ['format','checkstyle','spotbugs']:assert s['stages'][name]['actualExit']==0
assert s['stages']['pmd']['actualExit']==4
folder=sp.parent;cs=ET.parse(folder/'checkstyle.xml').getroot();assert not cs.findall('.//error')
pmd=ET.parse(folder/'pmd.xml').getroot();assert not [x for x in pmd.iter() if x.tag.rsplit('}',1)[-1] in ['error','processingerror']]
reasons={
 ('ArtifactComparator.java',74):'compare-local currentByCase TreeMap, passed only to current invocation semantic comparison; deterministic case order required',
 ('ArtifactComparator.java',75):'compare-local nkByCase TreeMap, no static publication, deterministic case ordering',
 ('ArtifactComparator.java',103):'compare-local allowlist rules LinkedHashMap preserves declared order, one invocation only',
 ('ArtifactComparator.java',253):'artifactFiles returns fresh TreeMap to current invocation only; deterministic file names, no shared worker mutation',
 ('CorrelatedLogEvidenceValidator.java',100):'expectations builds fresh event index for one immutable JSON input/validation; method-local, concurrency Test isolates calls',
 ('CorrelatedLogEvidenceValidator.java',167):'verifyRows creates fresh addedEvents from current before/after maps, no static/shared retention',
 ('CorrelatedLogEvidenceValidator.java',188):'rows creates fresh row-id index consumed only by same validation; independent concurrent calls tested',
 ('GateCli.java',128):'verifySource invocation-local ordered report actual map written by current invocation',
 ('GateCli.java',214):'preflight invocation-local ordered report map; no shared mutable result writer',
 ('GateCli.java',265):'compareCurrent local ordered aggregate result; thread confined to current report generation',
 ('GateCli.java',336):'report local ordered gate result; returns immutable/publicly serialized report, no cross-invocation mutable map',
 ('GateCli.java',496):'promoteCurrent creates one local deterministic manifest for owned synthetic destination; original baseline never passed',
 ('GateCli.java',560):'prefixed builds fresh sorted map from current parameter; no concurrent mutation contract',
 ('GateCli.java',566):'fileHashes builds fresh sorted path/hash map, consumed by current comparison only',
 ('GateContractValidator.java',124):'validate local ordered metrics map; ValidationResult copies immutable metrics and failures; concurrent independent trees tested'}
sites=[]
for f in pmd:
 if f.tag.rsplit('}',1)[-1]!='file':continue
 for v in f:
  if v.tag.rsplit('}',1)[-1]!='violation':continue
  key=(Path(f.get('name')).name,int(v.get('beginline')));assert key in reasons and v.get('rule')=='UseConcurrentHashMap'
  path=Path(f.get('name'));sites.append(dict(path=str(path.relative_to(r)),sourceSha256=sha(path),line=key[1],rule=v.get('rule'),decision='NOT_APPLICABLE_THREAD_CONFINED_ORDERED_VALUE',reason=reasons[key],evidence='PG37012 all124 including independent concurrent JSON/tree/file output tests; exact byte/source PG37016'))
assert len(sites)==len(reasons)==15
sb=ET.parse(folder/'spotbugsXml.xml').getroot();stats={x.get('class') for x in sb.findall('.//ClassStats')};expected={p[:-6].replace('/','.') for p in u['classSha256']};assert stats==expected and len(stats)==10
assert not sb.findall('BugInstance') and not sb.findall('.//MissingClass') and not sb.findall('.//Error')
assert all(v['missed']==0 for k,v in u['standardCounters'].items())
# No generated-code exclusion or private reflection is introduced to erase raw deficits.
assert u['rawCounters']['METHOD']['missed']==18 and u['rawCounters']['BRANCH']['missed']==34
out=b/'evidence/PG37020-p020-current-quality-join-v1';out.mkdir()
(out/'pmd-site-decisions.json').write_text(json.dumps(sites,ensure_ascii=False,indent=2)+'\n')
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceCore=u['sourceCore'],actualUnitSource=u['source'],run=u['run'],success=124,failed=0,errors=0,skipped=0,notRun=0,unitProof=ref(up),staticProof=ref(sp),formatErrors=0,checkstyleErrors=0,pmdRaw=15,pmdApplicable=0,pmdUnclassified=0,pmdDecisions=ref(out/'pmd-site-decisions.json'),spotbugs=dict(bugs=0,missing=0,errors=0,classStats=sorted(stats)),standardCounters=u['standardCounters'],rawCounters=u['rawCounters'],noNewSuppression=True,privateReflection=False,sourceBaselineUnchanged=True,oldSuccessReplayedForConfirmation=False,productTestsReexecuted=0,formalUpdated=False,newAcceptance=0,whole451Accepted=False,effortCompletionRate=None,remaining=['Raw18 methods/34branches5lines184instructions not credited as covered; constructor/record/enum/compiler cleanup review and meaningful PT/PG remains','P020 child01.01/02/03 and parent F02 dependency not accepted','Actual Current/NK capture/native/CHR remains separate held scope'],metadataCorrection='4560 stdout PMD issues0 was namespace-naive display only, original XML/exit4 immutable; independent namespace-aware total15 explicitly classified. No claim rawPMD0 or changed successful product test.')
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
l=r/'documents/900_OTHER/910_台帳'
with (l/'915_障害表.md').open('a') as f:f.write('\n2026-11-17 BUG3145 限定CLOSED。修正input/4559は元declared Test signatureを全17クラスで照合し、Path2/空引数115/文字列7variantの元124XML集合と完全一致、FESnotrun0及び負4をPG37016で確認。製品再演0、元失敗37014保存。修正commitは当inputのGit履歴、完了2026-11-17。PG37020へsource/全rawを横断反映。\n')
with (l/'916_横展開管理台帳.md').open('a') as f:f.write('\n2026-11-17 YKT2614 限定CLOSED。全124の元17Test宣言/出力をPG37016/casesへ一意join、TempDir引数2/空引数115/7variantを全件確認。未知element/failure/error/skip負4は拒否し、成功XML system-out/errは許容。実Test再演0、元失敗保全。修正input4559とPG37020のGit履歴、再試験証跡PG37016。\n')
print(json.dumps(dict(actualExit=0,success=124,fullMainPhysical=10,staticApplicable=0,unclassified=0,pmdRaw=15,raw=u['rawCounters'],newAcceptance=0)))
