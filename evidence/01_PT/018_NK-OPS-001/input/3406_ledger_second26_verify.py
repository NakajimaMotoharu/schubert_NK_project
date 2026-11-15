"""Scope-aware reconciliation of21 historical limited fixes and5 legitimate open holds; no product replay."""
from pathlib import Path
import json,re,hashlib,datetime,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';e=b/'evidence/PG33702-ledger-second26-scope-join-v1';assert not e.exists();load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));decisions=load(i/'3405_ledger_second26_decisions.json');catalog=load(b/'evidence/PG33700-ledger-second26-catalog-v1/candidate-catalog.json');rows={x['bug']:x for x in catalog['candidates'] if x['inCurrentBoundedMigrationReview']};assert set(rows)=={x['bug'] for x in decisions['rows']};public={}
# Read only enumerated public manifests; never their private payloads or original exec/classes.
for num in sorted({n for row in decisions['rows'] for n in row['proofPgIds']}):
 ds=[p for p in (b/'evidence').iterdir() if p.name.startswith('PG'+str(num)+'-')];assert len(ds)==1,(num,[p.name for p in ds]);p=ds[0]/'manifest.json';assert p.is_file(),num;public[num]=(p,load(p))
def zero(num):
 x=public[num][1];value=x.get('actualExit',x.get('actualExitCode'));assert type(value) is int and value==0,(num,value);return x
def positive(num,*fields):
 x=zero(num)
 for name in fields:assert x[name] is True,(num,name)
 return x
# Already completed five worker fixes, each original scope kept distinct.
for n,count in [(28090,7),(28112,18),(28136,28)]:
 x=positive(n,'completeSourceComponentFour100');assert x['tests']==count and x['staticApplicable']==x['unclassified']==x['processingErrors']==0
assert not zero(28112)['wholeScopeFour100'] and zero(28136)['wholeScopeFour100']
for n in [28076,28098,28120]:assert zero(n).get('MainChanged',False) is False
worker_names={'ApiNonSecretConfigTest.java','InternalErrorRouterPortTest.java','ErrorDispatchRouterPortTest.java','HttpMetricRecorderTest.java','HttpMetricContractTest.java'};worker_pins=[]
for n in [28090,28112,28136]:
 x=zero(n)
 for path,h in x['inputHashes'].items():
  if Path(path).name not in worker_names:continue
  p=Path(path);p=p if p.is_absolute() else r/p;assert p.is_relative_to(r/'src') and p.suffix=='.java';assert sha(p)==h,(n,path);worker_pins.append(dict(path=str(p.relative_to(r)),sha256=h,originalPost=n,source=x['source']))
assert {Path(x['path']).name for x in worker_pins}==worker_names and len(worker_pins)==5
# Source/style/tool-specific acceptance; never use a different result's success as its proof.
x=positive(29258,'artifactComparatorAllPhysicalFour100','baselineUnchanged','sourceInputsUnchanged');assert x['totalToolTests']==46 and (x['failures'],x['errors'],x['skipped'])==(0,0,0)
s=positive(29260,'rootRulesUnchanged');assert s['source']==x['source'] and all(s[k]==0 for k in ['applicable','unclassified','processingErrors','checkstyle'])
x=positive(29288,'wholeClass','sourceInputsUnchanged','targetFour100');assert (x['tests'],x['failures'],x['errors'],x['skipped'],x['newTestStaticApplicable'],x['newTestStaticUnclassified'])==(11,0,0,0,0,0)
x=positive(29478,'wholeOriginalSevenRetained','wholeOriginalSevenNormalizedInversePreserved','wholeClosureMeasuredFour100');assert (x['tests'],x['failures'],x['errors'],x['skipped'],x['heldClassInitializations'],x['heldClassPositiveProbes'])==(155,0,0,0,0,0) and x['productionCoreMain']=='8b539471183a640ad4a2541ee06a1eb1717199fc' and x['staticApplicable']==0
assert zero(29404)['productTestsExecuted']==0
x=zero(29690);assert x['otherDefaultDiffCheckExit']==x['limitedTwoPathDiffCheckExit']==x['secretPatternFindings']==0 and x['productTestsRun']==0
x=positive(29780,'onlyOwnSectionEofSeparatorChanged','otherDocumentTextUnchanged');assert x['removedTerminalLfCount']==2 and not x['rawEvidenceRewritten']
x=zero(29710);assert not x['TestExecution'] and not x['DBConnection'] and x['productTestsExecuted']==0
x=positive(29904,'allSixTargetsFixedOrReasonedAndSourceBound');assert x['formalAcceptanceAdded']==0
for n,count in [(29896,12),(30646,72),(31292,80),(31400,162)]:
 x=zero(n);assert (x['tests'],x['failures'],x['errors'],x['skipped'])==(count,0,0,0)
for n in [29898,30648,31294,31374,31402]:positive(n,'wholeScopeFour100')
x=positive(31298,'ordinaryMerge','upstreamPrefixPreserved');assert not x['implementationIncluded'] and x['mainCommit']=='8d15fe695578ef19b0f85a4ffbf70a37272b6c48' and len(x['paths'])==1 and x['paths'][0].endswith('/914_詳細設計修正管理台帳.md')
positive(31344,'fullLiteralControlInverse','productionMainUnchanged');positive(31360,'allQuotedLiteralAndNonWhitespaceTokensEqual','onlyFormattingChanged');positive(31386,'twoDeclarationStatementsSplitOnly','fullInverse','inputAndExpectedValuesUnchanged')
x=positive(31438,'allInputsUnchanged');assert (x['physicalClasses'],x['actualCodeMethods'],x['defaultMethods'],x['filteredMethodDifference'])==(16,137,112,25) and x['applicationTestsExecuted']==0
# All evidence checks precede ledger modifications; keep other issues inside a section untouched.
led=r/'documents/900_OTHER/910_台帳';paths={'BUG':led/'915_障害表.md','YKT':led/'916_横展開管理台帳.md'};before={k:p.read_text() for k,p in paths.items()};after=dict(before)
def section(s,prefix,num):
 m=re.search(r'^## '+prefix+'-'+str(num)+r'\b.*?(?=^## '+prefix+r'-|\Z)',s,re.M|re.S);assert m,(prefix,num);return m
changes=[]
def update(prefix,num,disposition,reason,proofnums):
 text=after[prefix];m=section(text,prefix,num);part=m.group();first=re.search(r'\n\n(\S[\s\S]*?)(?=\n\n|\Z)',part);assert first;oldbody=first.group(1);newbody=oldbody
 closed=disposition.startswith('HISTORICAL')
 if closed:
  newbody=re.sub(r'状態[:：]?\s*OPEN','起票時OPEN（履歴）',oldbody)
  # Preserve bare OPEN and foreign status paragraphs as history; canonical footer takes priority.
 result=part[:first.start(1)]+newbody+part[first.end(1):]
 state='CLOSED（既記載の限定対象のみ）' if closed else 'OPEN（'+disposition+'）'
 footer='\n2026-11-15 scope照合訂正（BUG2999/YKT2527、PG33702）：現行状態'+state+'。'+reason+' 元記録/失敗/途中OPENは履歴として保持し現在値へ流用しない。元公開manifest/hash/原source/run及び固有後条件を照合、新試験/新受入0。保持原本/actual4/Root2/VM/DB/native/aru/HOLDの操作・解除0。\n'
 result+=footer+'\n';assert result[:first.start(1)]==part[:first.start(1)] and result[first.start(1)+len(newbody):len(result)-len(footer)-1]==part[first.end(1):]
 after[prefix]=text[:m.start()]+result+text[m.end():];changes.append(dict(id=prefix+str(num),disposition=disposition,reason=reason,proofs=[ref(public[n][0]) for n in proofnums],beforeSha256=hashlib.sha256(part.encode()).hexdigest(),afterSha256=hashlib.sha256(result.encode()).hexdigest(),changedOnlyOwnFirstParagraphStateAndExplicitFooter=True,foreignIssueParagraphsUnchanged=True))
for decision in decisions['rows']:
 n=decision['bug'];assert hashlib.sha256(section(before['BUG'],'BUG',n).group().encode()).hexdigest()==rows[n]['originalSectionSha256']
 update('BUG',n,decision['disposition'],decision['scopeReason'],decision['proofPgIds'])
# Close only independently matched original YKT scopes; similarly numbered/related scopes stay open.
for num,bug in {2380:2725,2406:2857,2425:2893,2426:2894,2427:2895,2428:2896,2429:2897,2430:2898,2529:2738}.items():
 decision=next(x for x in decisions['rows'] if x['bug']==bug);update('YKT',num,'HISTORICAL_LIMITED_CLOSED_SYNC',decision['scopeReason'],decision['proofPgIds'])
for prefix in paths:
 selected={int(x['id'][len(prefix):]) for x in changes if x['id'].startswith(prefix)}
 for m in re.finditer(r'^## '+prefix+r'-(\d+)\b.*?(?=^## '+prefix+r'-|\Z)',before[prefix],re.M|re.S):
  if int(m.group(1)) not in selected:assert m.group()==section(after[prefix],prefix,int(m.group(1))).group()
for num in decisions['sharedYktToPreserve']:assert section(before['YKT'],'YKT',num).group()==section(after['YKT'],'YKT',num).group()
assert len(changes)==35
# New PGPT product sources and tests remain exactly as qualified at1050; no full regression needed.
post=load(b/'evidence/PG33682-copyverify1050-post-v1/manifest.json');pf=load(i/'3388_copyverify1050_profile.json');pins={}
for path in pf['mainSources']+[x['path'] for x in pf['testSources']]:assert sha(r/path)==post['inputHashes'][path];pins[path]=post['inputHashes'][path]
assert len(pins)==105
e.mkdir();report=dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source='ef461eba8bea80b4ed17f52d832094c139fef122',productionCoreMain='ef461eba8bea80b4ed17f52d832094c139fef122',decisions=ref(i/'3405_ledger_second26_decisions.json'),catalog=ref(b/'evidence/PG33700-ledger-second26-catalog-v1/candidate-catalog.json'),reviewedOriginalCandidates=26,priorReviewedOriginalCandidates=26,totalReviewedOriginalCandidates=52,remainingOriginalCandidates=173,bugLimitedStatusSync=21,validOpenPartialHold=5,yktLimitedStatusSync=9,newYkt2529ForDistinctFiveWorkerScope=True,relatedDifferentYkt2387Unchanged=True,changes=changes,publicProofManifests=[dict(pg=n,**ref(p),recordedExit=x.get('actualExit',x.get('actualExitCode'))) for n,(p,x) in public.items()],fiveCurrentTestPinsMatchOriginalWorkerQualifications=worker_pins,all105QualifiedJavaSourcePinsUnchanged=pins,originalFailureAndPartialEvidencePreserved=True,oldSuccessfulTestsReplayed=0,productTestsExecuted=0,newProductDefinitions=0,newAcceptance=0,whole451Accepted=False,formalUpdated=False,effortRate=None,bug2999Ykt2527RemainOpen=True)
(e/'manifest.json').open('x').write(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
for prefix,p in paths.items():p.write_text(after[prefix])
print(dict(actualExit=0,reviewed=26,bugLimitedSync=21,validOpenHolds=5,yktLimitedSync=9,newYkt2529=True,remainingCandidates=173,productTestsExecuted=0))
