"""Join final Tool-only ordinary tests/static while retaining full-bundle HOLD and source separation."""
from pathlib import Path
import datetime as dt
import hashlib,json,subprocess
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';E=B/'evidence';D=R/'documents/400_PGPT/470_PMO/600_通常PGPT_20261106';W=R.parent/'pgpt-runs/PG379';TC=R.parent/'toolchain'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p))
load=lambda p:json.loads(p.read_text())
def write(p,v):assert not p.exists();p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def normalized(s):return subprocess.check_output([str(TC/'jdk-25.0.4/bin/java'),'-jar',str(TC/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','-'],input=s.encode())
def main():
 post=E/'PG29258-chr-tool-independent-post-v1/manifest.json';m=load(post);st=E/'PG29260-chr-static-exact-applicability-v1/manifest.json';a=load(st);assert m['actualExitCode']==a['actualExitCode']==0 and m['source']==a['source']=='029c35c032291a2f93894713de37ef0387071ea9';assert m['totalToolTests']==46 and all(m[k]==0 for k in ('failures','errors','skipped')) and m['baselineUnchanged'] and m['sourceInputsUnchanged'] and a['unclassified']==a['applicable']==0 and not m['fullBundleAccepted'];assert all(int(c['missed'])==0 for ms in m['changedScannerMethodCounters'].values() for cs in ms.values() for c in cs)
 # Restore only newly added test block / literal pooling, then compare normalized old bytes.
 td=R/'program/characterization/tests/java/dev/codex/schubert/characterization';old=E/'PG29230-chr-tool-source-fix-v1';proof={}
 for name,marker in [('ArtifactComparatorTest','  /** PT-CHR-DIF015-001'),('GateContractTest','  /** PT-CHR-G06-STREAM-001')]:
  text=(td/(name+'.java')).read_text();end='  private Fixture fixture(' if name=='ArtifactComparatorTest' else '  private static JsonNode resource(';start=text.index(marker);text=text[:start]+text[text.index(end,start):]
  if name=='ArtifactComparatorTest':
   for ident,value in [('FIXTURE_DIF015','DIF-015'),('FIXTURE_OBSERVATIONS','observations'),('FIXTURE_EXPECTED_NK','expectedNk')]:
    declaration='  private static final String '+ident+' = "'+value+'";\n';assert text.count(declaration)==1;text=text.replace(declaration,'').replace(ident,'"'+value+'"')
  else:text=text.replace('import static org.junit.jupiter.api.Assertions.assertThrows;\n','')
  expected=(old/(name+'.before.java.txt')).read_text();assert normalized(text)==normalized(expected)
  proof[name]=dict(oldSha256=sha(old/(name+'.before.java.txt')),normalizedInverseEqual=True,oldMethods=8 if name=='ArtifactComparatorTest' else 7)
 for name in ('GateContractValidatorNegativeTest','TargetAdapterTest','CorrelatedLogEvidenceValidatorTest'):
  p=td/(name+'.java');assert p.read_bytes()==subprocess.check_output(['git','show','2fee0c9545149c8b3cd34d50e812b1de6dabd67c:'+str(p.relative_to(R))],cwd=R);proof[name]=dict(oldBodyBytesUnchanged=True,currentSha256=sha(p))
 c=load(B/'input/2271_chr_tool_fix_start.json');f=load(R/c['forecastRef']['path']);assert sha(R/c['forecastRef']['path'])==c['forecastRef']['sha256'];before=dict(f['revisedRemainingPp']);now=dt.datetime.now(dt.timezone.utc).isoformat();done={'low':.6,'base':1.8,'high':3.6};held={'low':.2,'base':.6,'high':1.2}
 for k,v in done.items():
  f['additionalCompletedWorkPp'][k]=round(f['additionalCompletedWorkPp'][k]+v,3)
  f['additionalDiscoveredRemainingPp'][k]=round(f['additionalDiscoveredRemainingPp'][k]-v,3);f['revisedRemainingPp'][k]=round(f['revisedRemainingPp'][k]-v,3)
 runs=[dict(source='5446d37e7345fa27fb27a46877230a532595dad6',run='PG29236',tests=46,success=46,failed=0),dict(source='a3d60098a657c0fb234670ef42f0505d92d5739d',run='PG29246',tests=46,success=45,failed=1),dict(source=m['source'],run='PG29254',tests=46,success=46,failed=0)]
 tech=dict(kind='TOOL_ONLY_2_MAIN_FIXES_WHOLE5_46_NORMAL_SUCCESS_FULL_BUNDLE_HOLD',toolSource=m['source'],productionCoreMain=c['source'],programMainChanged=2,appMainChanged=0,appUniqueMain98Unchanged=True,toolTestDefinitionsNew=2,toolCurrentSourceSuccess=46,toolHistoricalRunsThisGroup=runs,appRosterDelta=0,formalTests=1964,formalScopes=53,newAcceptance=0,effortCompletionRate=None,post=ref(post),static=ref(st),oldWholeTestOracleProof=proof,scannerAllChangedMethodsCounters=m['changedScannerMethodCounters'],comparatorAllPhysicalFour100=True,allPhysicalClasses=10,wholeScopeCounters=m['allCounters'],wholeBundleAccepted=False,heldWholeGateCliTests=12,capacityRequiredGiB=20,estimateCompleted=done,estimateHeld=held,actualAllocatedPp=None,N=None,T=None)
 f.update(revision='358-CHR_TWO_FIXES_NORMAL46_TOOL_ONLY_PARTIAL_FULL_BUNDLE_HOLD',atJST=now,previousForecast=c['forecastRef'],latestGroupTechnicalResult=tech)
 f.setdefault('toolUnitRunRoster',[]).extend(runs);f.setdefault('toolDefinitionHistory',[]).append(dict(newDefinitions=2,tests=['PT-CHR-G06-STREAM-001','PT-CHR-DIF015-001'],firstSource=runs[0]['source'],currentSource=m['source'],noTripleCountAcrossSources=True));f.setdefault('toolQualificationHeldPrice',[]).append(dict(groupId=c['groupId'],price=held,reason='Full tool source/run static/negative/coverage and GateCli whole12 capacity precondition unresolved; not formal/2 completion. Coordinate with originalP020/2 to avoid duplicate payment for reused verification.'))
 fp=D/'1477_WBS65予実・比較scan通常四十六後版358.json';write(fp,f)
 out=E/'PG29262-chr-tool-two-fixes-result-join-v1';out.mkdir(exist_ok=False);joined=dict(actualExit=0,atUTC=now,source=c['source'],productionCoreMain=c['source'],qualifiedToolSource=m['source'],post=ref(post),static=ref(st),technical=tech,formalAcceptanceAdded=0,fullBundleAccepted=False);write(out/'manifest.json',joined)
 description='比較Tool2Mainを是正、source029c35c032固定でwhole5/46全成功・F/E/skip0、PG29258独立post0。全5Main/10physical除外0、Scanner3method I222/L44/M3/B36 miss0、Comparator2physical全四100。RootJava25offline build/Spotless0、SBbugs/missing/errors0、CS0、PMD生22は各site根拠で適用0/未分類0・元report保持。全scope L350/M37/C2/B200未網羅は保持しGateCli whole12実20GiB前提HOLD、bundle100/451/実CHR未受入。旧44invocation期待値の逆変換/不変更一致、新2定義のみ。PG29246は追加oracleの未規定列挙順仮定で46中1失敗、修正後sourceだけ再試験、元失敗保持。BUG2811/2812限定是正・2813/14/15/16工具/試験是正を証跡へ対応。source src eeba/Main98不変、実Root/VM/DB/HTTP/Browser/native/credential/master0。価格.6/1.8/3.6のみ計画完了、残.2/.6/1.2を全工具資格へ保持、実費/工数ではない。正式1964-53/元190新0/工数null。'
 result=R/'evidence/01_PT/020_NK-CHR-001/012_NK-CHR-001_比較scan二是正・通常四十六結果.md';assert not result.exists();result.write_text('# NK-CHR-001 比較scan二是正・通常四十六結果\n\n'+description+'\n\n仕様：[011_NK-CHR-001_比較scan二是正・通常工具試験仕様.md](011_NK-CHR-001_比較scan二是正・通常工具試験仕様.md)。run PG29254 / Toolsource '+m['source']+'。独立post '+str(post.relative_to(R))+' SHA256 '+sha(post)+'。全XML/command/時刻/exit/input/sourcebyte/physicalhash/静的指摘/counterは上記manifest群。Currentbaseline27file前後不変。元5446成功46を現sourceへ足さない。App試験rosterは87/3869/3840/29のまま、Tool46を別列で記録する。\n')
 art=R/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json';v=load(art)
 for item in v['artifacts']:
  if item['path'] in c['toolImplementationArtifactPaths']:
   item['sha256']=sha(R/item['path']);item['currentLimitedToolVerification']=dict(toolSource=m['source'],run='PG29254',evidence=ref(post),fullToolBundleAccepted=False,formalAcceptanceAdded=0)
 art.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');cov=R/'documents/400_PGPT/470_PMO/486_WBS現行実績.json';v=load(cov);assert 'inventorySha256' in v;v['inventorySha256']=sha(art);cov.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
 nextcmd='Price currentCorrelatedLogEvidenceValidator whole9 original plus missing QA054 ACTION pairs/strict-shape/responseBytes independent cases; use pureJSON ownedfixture/wholeclass, no DB/realcapture/authority replacement. Before edits review actual same-source missed branch lines and current owner/criteria. Hold fullGateCli12 actual20GiB capacity and originalP020/2, preserve partial fullbundle misses and baseline. Other independentPGPT continues, no same success confirmation replay.'
 ec=dict(groupId=c['groupId'],recordPath=str((D/'1478_WBS65比較scan二是正通常四十六結果.json').relative_to(R)),manifestPath=str((out/'manifest.json').relative_to(R)),manifestSha256=sha(out/'manifest.json'),terminalAtUTC=now,run='PG29262',workIds=c['workIds'],outcome='TWO_TOOL_FIXES_NORMAL46_SUCCESS_PARTIAL_PRICE_FULL_BUNDLE_HOLD',technical=tech,forecastRef=ref(fp),checkpointText=description,nextCommand=nextcmd);write(B/'input/2276_chr_tool_close.json',ec)
 print(json.dumps(dict(actualExit=0,toolSource=m['source'],normal46=True,oldOracleProof=True,remaining=f['revisedRemainingPp'],formalNew=0)))
if __name__=='__main__':main()
