"""Independent target byte/CRC and typed-list source proof guards; no JVM/Test replay."""
from pathlib import Path
import datetime,hashlib,json,zipfile,copy,struct
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';P=R/'evidence/01_PT/002_NK-PRO-002/evidence';I=B/'evidence/PG23768-changed-five-existing-proof-binding-v1';O=B/'evidence/PG23770-changed-five-existing-proof-independent-v1';load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');assert not O.exists();m=load(I/'manifest.json');assert sha(I/'manifest.json')=='27aa4298cc99ffcbc10d0c340dff0353da5926c517830178805053980b12dbf4';cfg=load(R/m['config']['path']);assert sha(R/m['config']['path'])==m['config']['sha256']
for n,pin in cfg['publicInputs'].items():assert sha(R/n)==pin
for n,pin in m['artifacts'].items():assert sha(I/n)==pin
idx=load(B/'evidence/PG23360-base59-named-proof-supplement-v1/current-normal-physical-index.json');normal=load(Path(cfg['currentNormalManifest']['path']));rows=load(I/'source-bindings.json');bindings=load(I/'physical-bindings.json');assert len(rows)==5 and len(bindings)==13;proto=load(P/'PG19458-qa054-protocol-selected-v1/manifest.json');metric=load(B/'evidence/provisional/PG14452-http-metric-whole-twenty-eight-post-v1/manifest.json');trace=load(P/'PG21852-current-protocol-four-source-existing-proof-trace-v1/manifest.json');assert proto['heldFourInitializationHits']==0
def empty_list(value):assert type(value) is list and not value
empty_list(proto['manualCoverageExclusions']);empty_list(metric['manualCounterExclusions']);assert proto['oldExecUnion'] is False and metric['oldCoverageTransferred'] is False
checks=0
for bad in [False,None,0,'',{},(),[1]]:
 try:empty_list(bad)
 except AssertionError:checks+=1
 else:raise AssertionError('non-list or nonempty exclusion value accepted')
def crc(raw):
 v=0
 for byte in raw:
  v^=byte
  for _ in range(8):v=(v>>1)^0xd800000000000000 if v&1 else v>>1
 return f'{v:016x}'
def access(raw):
 assert raw[:4]==b'\xca\xfe\xba\xbe';at=10;count=int.from_bytes(raw[8:10],'big');i=1
 while i<count:
  tag=raw[at];at+=1
  if tag==1:ln=int.from_bytes(raw[at:at+2],'big');at+=2+ln
  elif tag in (3,4,9,10,11,12,17,18):at+=4
  elif tag in (5,6):at+=8;i+=1
  elif tag in (7,8,16,19,20):at+=2
  elif tag==15:at+=3
  else:raise AssertionError('unknown class constant')
  i+=1
 return int.from_bytes(raw[at:at+2],'big')
seen=set();filtered=0;total={k:0 for k in ['LINE','METHOD','CLASS','BRANCH']}
for row in rows:
 p=row['mainPath'];assert sha(R/p)==row['currentMainSha256']==cfg['selectedCurrentSources'][p];physical={k for k,v in idx.items() if v['path']==p};assert physical==set(row['currentNormalPhysical']);group=[x for x in bindings if x['mainPath']==p];assert len(group)==len(physical) and {x['physicalClass'] for x in group}==physical;module=p.split('/')[1].removeprefix('schubert-nk-');jar=Path(normal['jars'][module]['path']);assert sha(jar)==normal['jars'][module]['sha256']
 with zipfile.ZipFile(jar) as z:
  for part in group:
   n=part['physicalClass'];raw=z.read(n+'.class');assert n not in seen;seen.add(n);assert hashlib.sha256(raw).hexdigest()==part['normalSha256']==part['originalQualifiedSha256']==idx[n]['sha256'];assert crc(raw)==part['currentCrc64']==part['originalProbeCrc64']==idx[n]['crc64'];assert part['physicalRetained'] and not part['manualExclusion'] and not part['productClassLoaded']
   if part['originalDefaultFiltered']:assert access(raw)&4096;filtered+=1
   originalCrc=proto['physicalClassIds'][n] if module=='protocol' else metric['executable'][n]['crc64'];assert originalCrc==part['originalProbeCrc64']
 if module=='protocol':original=next(x for x in trace['rows'] if x['path']==p)['originalSourceFileCounters']
 else:original=metric['fullSourceUnits']['dev/codex/schubert/nk/web/monitoring/HttpMetricContract']['totals']
 counters={k:original.get(k,dict(covered=0,missed=0)) for k in total};assert counters==row['originalSourceFileCounters'] and all(v['missed']==0 for v in counters.values());assert row['branchRatio']==(100 if counters['BRANCH']['covered'] else None) and row['currentTestSourceExecuted'] is False and row['newTests']==row['newAcceptance']==0
 for k in total:total[k]+=counters[k]['covered']
assert filtered==2 and total==m['originalCounterArithmeticReferenceOnly']==dict(LINE=781,METHOD=117,CLASS=11,BRANCH=413)
# Other two immutable schemas keep their declared bool/int values, not the changed list rule.
p=B/'evidence/provisional/PG9756-outbox-value-post-v3/manifest.json';outbox=load(p);assert outbox['exclusionsAdded'] is False
p=B/'evidence/provisional/PG6930-current4222-cases/qualification.json';old=load(p);assert type(old['FESFlakyNotRun']) is int and old['FESFlakyNotRun']==0
assert m['actualExit']==m['newProductTests']==m['productTestsExecuted']==m['actualBackendActions']==m['productClassesInitialized']==m['newAcceptance']==0
for name in ['combinedExecOrCoverage','originalTestsReexecuted','currentTestSourceExecuted','currentWholeSourceRunQualified','compilerOrJvmExecuted','protectedPathsRead','privateOriginalRunRead','formalUpdated','whole451Accepted']:assert m[name] is False
O.mkdir();out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),status='FIVE_EXISTING_TARGET_CODE_PROOFS_EXACT_BYTE_CRC_HISTORICAL_CONTEXT_ONLY',producer=dict(path=str((I/'manifest.json').relative_to(R)),sha256=sha(I/'manifest.json')),currentCoreMain=cfg['currentCoreMain'],targetSourceFiles=5,physicalClasses=13,originalEligibleClasses=11,originalDefaultFilteredSyntheticClasses=2,originalArithmeticCountersOnly=total,originalSeparateRuns=2,originalProbeCrcExactMatches=13,currentWholeSourceRunQualified=False,currentTestSourceExecuted=False,combinedExecOrCoverage=False,metadataNegativeChecks=checks,crossExpansionSchemas=dict(protocolExclusions='STRICT_EMPTY_LIST',httpExclusions='STRICT_EMPTY_LIST',outboxExclusionsAdded='EXACT_BOOLEAN_FALSE_NON_APPLICABLE',oldWholeFes='EXACT_INT_ZERO_NON_APPLICABLE'),bugs=['BUG-2497'],horizontal=['YKT-2235'],newProductTests=0,productTestsExecuted=0,productClassesInitialized=0,actualBackendActions=0,compilerOrJvmExecuted=False,protectedPathsRead=False,newAcceptance=0,formalUpdated=False,whole451Accepted=False,effortRate=None,tool=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))));write(O/'manifest.json',out);print(json.dumps(dict(actualExit=0,sources=5,physical=13,probeCrcMatches=13,metadataNegatives=checks,newTests=0,manifestSha256=sha(O/'manifest.json'))))
