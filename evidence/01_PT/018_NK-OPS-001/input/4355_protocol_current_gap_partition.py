"""Partition a pinned current raw manifest without reading or defining production classfiles."""
from pathlib import Path
from collections import Counter, defaultdict
import datetime, hashlib, json, subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
raw=b/'evidence/PG36284-ssc445-registry-unfiltered-v2/manifest.json';v=json.loads(raw.read_text())
cfg=json.loads((b/'input/4354_protocol_current_gap_start.json').read_text());pin=cfg['oracleRefs'][1]
assert ref(raw)==pin
core='7f04f07fb43c6fac322808fa3251d4f1b95e44ae';unit='5b12c4089ca1f59407529596e3e650aac513392c'
assert v['productionCoreMain']==core and v['actualUnitSource']==unit and v['actualExit']==0
assert v['oldExecCombined'] is False and v['allCurrentSourceInputsUnchanged'] is True
missing=v['missedCodeMethods'];assert len(missing)==33
branches=[m for m in v['methods'] if m['counters']['BRANCH']['missed']>0]
assert len(branches)==17 and sum(m['counters']['BRANCH']['missed'] for m in branches)==59
ctor=[m for m in missing if m['name']=='<init>'];values=[m for m in missing if m['name']!='<init>']
assert len(ctor)==6 and len(values)==27 and len({m['className'] for m in values})==10
maps=[m for m in v['methods'] if m['className'].endswith('$1') and m['counters']['INSTRUCTION']['missed']>0]
assert len(maps)==4 and sum(m['counters']['INSTRUCTION']['missed'] for m in maps)==16
witness=[];owners={x['path']:x['owner'] for x in json.loads((r/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_text())['artifacts']}
for name in sorted({m['className'].split('$')[0] for m in missing+branches+maps}):
 p=r/'src/schubert-nk-protocol/src/main/java'/(name+'.java')
 rel=str(p.relative_to(r));original=subprocess.check_output(['git','show',core+':'+rel])
 assert p.read_bytes()==original
 witness.append(dict(path=rel,sha256=sha(p),owner=owners[rel],currentCoreByteExact=True))
byname=defaultdict(list)
for m in values:byname[m['className']].append(m['name'])
bybranch=Counter({m['className']+'#'+m['name']+m['descriptor']:m['counters']['BRANCH']['missed'] for m in branches})
assert sum(bybranch.values())==v['protocolAllPhysicalRawCounters']['BRANCH']['missed']
assert sum(m['counters']['METHOD']['missed'] for m in missing)==v['protocolAllPhysicalRawCounters']['METHOD']['missed']
e=b/'evidence/PG36300-current-protocol-raw-gap-partition-v1';e.mkdir()
output=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source=core,productionCoreMain=core,actualUnitSource=unit,originalRawManifest=ref(raw),originalSingleExec=v['originalSingleExec'],rawCounters=v['protocolAllPhysicalRawCounters'],missingMethodCount=33,valueContractMissingMethods=values,valueContractClasses=dict(byname),unusedUtilityConstructors=ctor,partiallyMissedBranchMethods=branches,compilerSwitchMapMisses=maps,sourceWitness=witness,methodPartitionsDisjoint=True,branchSumIndependentlyReconciled=True,physicalClassfilesReadOrDefined=0,applicationTestsExecuted=0,oldExecCombined=False,formalUpdated=False,newAcceptance=0,effortRate=None,globalBug='BUG3111',globalYkt='YKT2583',globalState='OPEN',nextOrdinaryWork=[dict(id='WIRE_METADATA_VALUES',classes=['ExpectedRoute','TransportMetadata','LargeResultContent'],requirements='Independent fixed constructor inputs; explicit getters/rendering; real typed Map lookup with separately constructed equal keys, null/other type and unequal component keys. Retain original whole constructor/negative fixtures and source pins. No JMS/backend operation.'),dict(id='PAYLOAD_MODEL_VALUES',classes=['CommonHeader','FieldDefinition','LayoutDefinition','LayoutFields','PayloadValues','TypedPayloadValues','WireMessage'],requirements='Independent SS offsets/lengths/fields and immutable list inputs. Preserve redacted toString. WireMessage pairs share one immutable FixedPayload identity while wrappers are independent. FieldDefinition has separate switch branch gap; value API tests alone cannot qualify entire class.'),dict(id='UTILITY_AND_BRANCH_RESPONSIBILITIES',requirements='Six private utility constructors require SS responsibility review before PG, preserve public API/actual cached-state ownership. Seventeen branch methods retain independent error/boundary expectations. Four javac switch-map code gaps remain explicit; no filter/exclusion or impossible enum injection.')])
(e/'manifest.json').open('x').write(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
(e/'next-ordinary-work.md').open('x').write('# 現Protocol raw残作業\n\n33未hit method = 十値classの27method + 六utility constructor。59未hit branchは17method、別に四compiler mapの16instruction。元rawの同source単一execから照合し再実行0。\n\n'+''.join('- '+x['id']+': '+x['requirements']+'\n' for x in output['nextOrdinaryWork'])+'\n全体BUG3111/YKT2583はOPEN。正式認定/工数率を変更しない。\n')
print(json.dumps(dict(actualExit=0,missingMethods=33,valueMethods=27,utilityConstructors=6,branchMethods=17,missingBranches=59,compilerMaps=4,sourceWitnesses=len(witness),applicationTests=0)))
