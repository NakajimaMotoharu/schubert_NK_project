"""Reconcile26 already explicitly closed migration records from immutable public proofs; no test replay."""
from pathlib import Path
import hashlib,json,re,datetime,subprocess,sys,platform
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';e=b/'evidence/PG33696-ledger-status-26-evidence-join-v1';assert not e.exists();load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));catalog=b/'evidence/PG33694-ledger-status-dated-catalog-v1/candidate-catalog.json';c=load(catalog);assert c['independentToolParserChecks']==10 and c['candidateCount']==225 and not c['ledgerWritten'];rows=[x for x in c['candidates'] if x['inCurrentBoundedMigrationReview']];assert [x['bug'] for x in rows]==list(range(2900,2926));cache={}
for row in rows:
 for item in row['originalPublicManifestRefs']:
  p=r/item['path'];assert str(p.relative_to(b/'evidence')).endswith('/manifest.json') and sha(p)==item['sha256'];cache[item['path']]=load(p)
def at(num):
 matches=[v for k,v in cache.items() if Path(k).parent.name.startswith('PG'+str(num)+'-')];assert len(matches)==1;return matches[0]
def yes(num,*keys):
 x=at(num);assert x['actualExit']==0
 for key in keys:assert x[key] is True,(num,key)
 return x
# Tool/annotation-specific claims checked separately: product PASS is not a substitute.
x=yes(31472,'allInputsUnchanged');assert (x['physicalClasses'],x['actualCodeMethods'],x['defaultMethods'],x['filteredMethodDifference'])==(17,134,90,44)
yes(31484,'allOldTokensAfterLiteralExpansionMatch','mainBytesUnchanged')
x=yes(31558,'allOld399TestBodiesPrefixExact','allMainStringLiteralsUnchanged','allOtherMainAndTestSourcesUnchanged');assert (x['totalMainFiles'],x['changedMainFiles'],x['unchangedMainFiles'],x['totalOriginalTestFiles'],x['changedOriginalTestFiles'],x['unchangedOriginalTestFiles'])==(21,2,19,22,2,20)
yes(31622,'allOriginalTokensAfterConstantExpansionExact','allMainBytesUnchanged')
yes(31642,'recoveredOnlyMissingManifestAndStartConfig','allExistingMetadataRetained','allExpectedMetadataAndBudgetReconciled','pureRelativeAbsolutePathBindingAndOutsideRejection')
yes(31686,'exactInverse','astInputNeverUsedAsOutput');yes(31692,'allOld24MainAnd459DefinitionsUnchanged');assert at(31692)['priorTestUnit']=='f40046a42b1c2c5d59472e2a9f2a1d3b0752bc20'
yes(31710,'exactInverse');yes(31726,'allLiteralAndNonspaceTokensUnchanged');x=yes(31746,'originalStaticUnchanged');assert (x['oldSameByteSites'],x['newFiniteWorkerSites'],x['newMemorySinkSites'])==(153,5,1)
yes(31772,'literalExtractionInverseTokensEqual','exactPhaseCloseTuplesAdded','exactResultShapeCloseTuplesAdded');yes(31792,'exactInverse','nullableVendorCheckPreserved','sqlAndDiagnosticsUnchanged','testSourceUnchanged')
x=yes(31542);assert all(x['spotbugs'][k]==0 for k in ['bugs','missing','errors'])
for num,count in [(31502,129),(31546,399),(31568,403),(31632,132),(31676,96),(31736,383),(31802,411),(31826,403),(31870,543),(31914,403),(31938,156),(31984,176),(32046,553)]:
 x=yes(num);assert (x['tests'],x['failures'],x['errors'],x['skipped'])==(count,0,0,0)
pairs=[]
for postnum,rawnum,source in [(31504,31508,'a7cd3daf395c07536e2dd10421b0173e703a265b'),(31570,31572,'443b9df7ec17ca2aaf0e8c025221279b905a19cf'),(31634,31636,'578eefe05af81bad69e3252177688dbe1ba4aee8'),(31678,31680,'f40046a42b1c2c5d59472e2a9f2a1d3b0752bc20'),(31738,31740,'2c7bf442914100b852823a3e07c307be1b975c4e'),(31804,31806,'3547449c651107c0e4526376f911ba8ef74fb0d8'),(31828,31830,'7aa390ed9c04955bf5fd2f1cc8eb9d67cc0317dc'),(31872,31874,'3d9fb2c0a430a42e159aafa1de73926aaffae6e9'),(31916,31918,'e4461ebb70a91c2e3717de12cd1a62ad608f14dc'),(31940,31942,'6abbb4ec5ee99978be260f59fe534d8c12aa0f9a'),(31986,31988,'8ce04bd1ed579a789eca4b7679c2d5ac970304a5'),(32048,32050,'7fbdce9f1004cf09a2899d39b04ffa467ab5e50c')]:
 p=yes(postnum,'wholeScopeFour100');raw=yes(rawnum,'rawFour100');assert p['source']==raw['actualUnitSource']==source;pairs.append(dict(post=postnum,raw=rawnum,originalUnitSource=source,defaultRawFour100=True))
# All proof checks above precede any ledger writes.
led=r/'documents/900_OTHER/910_台帳';paths={name:led/name for name in ['915_障害表.md','916_横展開管理台帳.md']};before={name:p.read_text() for name,p in paths.items()};after=dict(before);edits=[];ykt_to_bug={2432:2900,2433:2902,2434:2903,2435:2904,2436:2905,2437:2907,2438:2908,2439:2909,2440:2910,2441:2911,2442:2912,2443:2913,2444:2914,2445:2915,2446:2916,2447:2917,2448:2918,2449:2919,2450:2920,2451:2921,2452:2922,2453:2923,2454:2924,2455:2925};open_pattern=r'状態OPEN|状態[:：]\s*OPEN'
def section(s,prefix,num):
 m=re.search(r'^## '+prefix+'-'+str(num)+r'\b.*?(?=^## '+prefix+r'-|\Z)',s,re.M|re.S);assert m;return m
for name,prefix,targets in [('915_障害表.md','BUG',{x['bug']:x['bug'] for x in rows}),('916_横展開管理台帳.md','YKT',ykt_to_bug)]:
 for num,bug in targets.items():
  s=after[name];m=section(s,prefix,num);part=m.group();row=next(x for x in rows if x['bug']==bug)
  if prefix=='BUG':assert hashlib.sha256(part.encode()).hexdigest()==row['originalSectionSha256']
  else:assert part==section(subprocess.check_output(['git','show',c['originalHead']+':'+str(paths[name].relative_to(r))],text=True),prefix,num).group()
  old_states=re.findall(open_pattern,part);assert old_states,(prefix,num)
  changed=re.sub(open_pattern,'当時OPEN（履歴。現在の限定解決は末尾参照）',part)
  addition='\n2026-11-15 記録整合訂正（BUG2999/YKT2527）：現行状態CLOSED（元2026-11-14記載の当対象限定解決と同範囲、全工程/実環境HOLDを解除しない）。根拠PG33694/PG33696の元paragraph SHA・公開manifest SHA・原source/run/終了・default/raw/工具固有後条件照合。既記載完了日/修正commitを保持し、新しい製品試験・再認証・受入は0。元OPENと過去の失敗/途中未達は履歴として残す。\n'
  changed=changed.rstrip()+'\n'+addition+'\n';after[name]=s[:m.start()]+changed+s[m.end():];edits.append(dict(ledger=name,id=prefix+str(num),mappedBug=bug,originalSectionSha256=hashlib.sha256(part.encode()).hexdigest(),correctedSectionSha256=hashlib.sha256(changed.encode()).hexdigest(),oldOpenOccurrences=len(old_states),closureParagraphSha256=row['closureParagraphSha256'],status='HISTORICAL_LIMITED_CLOSED_SYNCHRONIZED_NOT_NEW_ACCEPTANCE',publicProofs=row['originalPublicManifestRefs']))
# Shared generated-Code campaign is explicitly not closed by one Scenario target.
assert section(before['916_横展開管理台帳.md'],'YKT',2431).group()==section(after['916_横展開管理台帳.md'],'YKT',2431).group()
assert len(edits)==50 and sum(x['id'].startswith('BUG') for x in edits)==26 and sum(x['id'].startswith('YKT') for x in edits)==24
for name in paths:
 # Changes are only the selected sections, not other IDs or the new still-open global rework.
 old=before[name];new=after[name];prefix='BUG' if name.startswith('915') else 'YKT';changednums={int(x['id'][len(prefix):]) for x in edits if x['ledger']==name}
 for m in re.finditer(r'^## '+prefix+r'-(\d+)\b.*?(?=^## '+prefix+r'-|\Z)',old,re.M|re.S):
  if int(m.group(1)) not in changednums:assert m.group()==section(new,prefix,int(m.group(1))).group()
 # Only raw status strings change, with explicit new footer; all original non-status content retained.
 for row in [x for x in edits if x['ledger']==name]:
  oldpart=section(old,prefix,int(row['id'][len(prefix):])).group();newpart=section(new,prefix,int(row['id'][len(prefix):])).group();assert re.sub(open_pattern,'',oldpart).strip() in newpart.replace('当時OPEN（履歴。現在の限定解決は末尾参照）','')
e.mkdir();report=dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),originalHead=c['originalHead'],productionCoreMain='ef461eba8bea80b4ed17f52d832094c139fef122',catalog=ref(catalog),originalCandidateCount=225,bugStatusCorrections=26,yktStatusCorrections=24,remainingOriginalCandidates=199,allRemainingCandidatesUnreviewedNotDeclaredUnresolved=True,scopeQualifiedExistingClosureOnly=True,explicitSameSourcePostRawPairs=pairs,originalPublicManifests=[dict(path=k,sha256=sha(r/k),actualExit=v.get('actualExit')) for k,v in cache.items()],edits=edits,sharedYkt2431Unchanged=True,bug2999AndYkt2527RemainOpen=True,parser10IndependentChecks=True,failedHistoricalRunsPreserved=True,sourceJavaOrTestChanged=False,productTestsExecuted=0,newAcceptance=0,formalUpdated=False,effortRate=None,python=sys.version.split()[0],os=platform.platform())
(e/'manifest.json').open('x').write(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
for name,p in paths.items():p.write_text(after[name])
print(dict(actualExit=0,bugCorrections=26,yktCorrections=24,remainingOriginalCandidates=199,productTestsExecuted=0,newAcceptance=0,sharedYkt2431Unchanged=True))
