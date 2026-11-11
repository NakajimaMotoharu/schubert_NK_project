"""Independent owner/source ending; global YKT29 remaining does not become acceptance."""
from pathlib import Path
import collections,datetime,hashlib,json,xml.etree.ElementTree as E
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';O=B/'evidence/PG26328-media-ending-independent-v1';assert not O.exists();load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();p=B/'evidence/PG26326-media-criteria-ykt35-dispositions-v1/manifest.json';assert sha(p)=='03908d5bb6513050ad50ddafd03af22b5914d6ed940bbd50b77a52eebdd74382';m=load(p)
for n,h in m['files'].items():assert sha(p.parent/n)==h
full=R/m['fullCurrentProtocolProof']['path'];assert sha(full)==m['fullCurrentProtocolProof']['sha256'];fm=load(full);assert fm['source']==m['source'] and fm['singleSession']==m['run'] and fm['tests']==130 and fm['actualExit']==0
for k,v in [('LINE',104),('METHOD',23),('CLASS',4),('BRANCH',81)]:assert m['coverage'][k]==dict(covered=v,missed=0)
rows=load(p.parent/'media-source-physical-counters.json');assert len(rows)==5 and len({x['path'] for x in rows})==4
for row in rows:assert sha(R/row['path'])==row['sourceSha256']
# Current owner standard-filter reasons are inherited only where authored behavior is unchanged.
previous=load(B/'evidence/PG26262-record-descriptor-time-criteria-v1/default-filter-review.json');filters=[x for x in previous if x['owner']=='WBS-P003-02'];assert len(filters)==9
for f in filters:
 src=(R/f['source']).read_text()
 if f['reason']=='PRIVATE_EMPTY_UTILITY_CTOR_STANDARD_FILTER':assert 'private MediaDescriptorValidator() {}' in src
 assert f['measuredRuntimeCoverageClaimed'] is False
sourceOwnerRows=load(B/'evidence/PG26176-six-domain-initial-owner-join-v1/current-owner-and-ending-gaps.json');byPath={}
for owner in sourceOwnerRows:
 for path in owner['sourcePaths']:assert path not in byPath;byPath[path]=owner['owner']
dispositions=load(p.parent/'ykt35-source-dispositions.json');assert len(dispositions)==35 and len({x['path'] for x in dispositions})==35
for row in dispositions:assert sha(R/row['path'])==row['sha256'] and row['path'] in byPath;row['costOwner']=byPath[row['path']];row['feeRule']='Retain existing original owner contract/quality work; no source-shared implementation double fee.'
count=collections.Counter(x['status'] for x in dispositions);unknown=sum(x['status'].startswith('PENDING') for x in dispositions);guarded=sum(x['status'] in ['EXISTING_STRICT_ENCODER_GUARD_SOURCE_NONAPPLICABLE','EXISTING_SURROGATE_GUARD_SOURCE_NONAPPLICABLE'] for x in dispositions);fixed=sum(x['status']=='CORRECTED_AND_RETESTED_CURRENT_SOURCE' for x in dispositions);nonapp=sum(x['status'] in ['ASCII_ALLOWLIST_OUTPUT_NOT_CANONICAL_VALUE_FACTORY','UTF8_READER_OUTPUT_NOT_RAW_UTF16_FACTORY'] for x in dispositions);assert (unknown,guarded,fixed,nonapp)==(18,11,3,3) and fixed+nonapp+unknown+guarded==35
O.mkdir();data={'all35-current-owner-dispositions.json':dispositions,'standard-nine-filter-review.json':filters}
for n,v in data.items():(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],productionCoreMain=m['productionCoreMain'],run=m['run'],owner='WBS-P003-02',currentHostCriteriaVerified=3,currentHostCriteriaTotal=3,ownerCoverage=m['coverage'],sourceArtifacts=4,physicalClasses=5,sameRunOwnerCases=11,defaultGeneratedFilterReasons=9,manualExclusionsAdded=0,globalYkt2328=dict(allSources=35,byteSites=41,localCorrectedRetested=3,sameCauseSourceNonApplicable=3,callerReachabilityOrContractUnconfirmed=18,existingGuardNormalWitnessBindingPending=11,totalGlobalClosurePending=29,closed=False),parent18CounterIsOnlyUnclassifiedStatusNotWholeRemaining=True,globalBug2648Closed=False,formalUpdated=False,whole451Accepted=False,newOriginal190Acceptance=0,productTestsExecuted=0,effortRate=None,parentManifest=dict(path=str(p.relative_to(R)),sha256=sha(p)),files={n:sha(O/n) for n in data},command='python3 -B evidence/01_PT/018_NK-OPS-001/input/1193_media_ykt_independent_post.py',toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,hostCriteria=3,yktPending29=True,newOriginalAcceptance=0,manifestSha256=sha(O/'manifest.json'))))
