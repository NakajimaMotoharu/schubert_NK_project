"""Close measured159 scope, preserve heterogeneous original31 run records and actual coverage gaps."""
from pathlib import Path
import datetime,hashlib,json
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';D=R/'documents/400_PGPT/470_PMO/600_通常PGPT_20261106'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text());ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
p=B/'evidence/PG27060-user-query159-independent-v1/manifest.json';m=load(p);assert m['actualExit']==0 and m['tests']==159 and m['requestAllFour100'] and not m['wholeScopeFour100']
o=B/'evidence/PG27062-user-query159-scope-result-v1';v=load(o/'manifest.json');assert v['source']==m['source'] and v['post']==ref(p)
old=next(D.glob('818_*'));f=load(old)
def numbers(row):
 cs=set(row)&{'actualExecutions','actualTests','tests'};ss=set(row)&{'success','successful'}
 if len(cs)!=1 or len(ss)!=1:raise ValueError('ambiguous or missing explicit historical count')
 result=(row[next(iter(cs))],row[next(iter(ss))],row['failed'])
 if any(type(x) is not int or x<0 for x in result) or result[0]!=result[1]+result[2]:raise ValueError('invalid observed counts')
 return result
before=f['knownObservedProductRunRoster'];assert len(before)==31
totals=tuple(sum(numbers(x)[i] for x in before) for i in range(3));assert totals==(2647,2639,8)
for bad in [{'unknownCount':1,'success':1,'failed':0},{'tests':1,'actualTests':1,'success':1,'failed':0},{'tests':1,'failed':0}]:
 try:numbers(bad)
 except ValueError:pass
 else:raise AssertionError('bad roster metadata admitted')
new=dict(source=m['source'],productionCoreMain=m['productionCoreMain'],run=m['run'],actualExecutions=159,success=159,failed=0,newTestDefinitions=0,evidence=ref(p),scope='EXPLICIT_WHOLE_USERQUERY17_CURRENT_DEPS142_REQUEST100_REPOSITORY_PARTIAL_NOT_FORMAL')
assert all(x.get('run')!=new['run'] for x in before);before.append(new)
f['knownObservedProductRunTotals']=dict(runs=32,actualExecutions=sum(numbers(x)[0] for x in before),success=sum(numbers(x)[1] for x in before),failed=sum(numbers(x)[2] for x in before),scope='EXPLICIT_OBSERVED32_RUN2806_EXEC_ONLY_NOT_GLOBAL_UNIQUE_OR_FORMAL')
assert f['knownObservedProductRunTotals']['actualExecutions']==2806 and f['knownObservedProductRunTotals']['success']==2798
f['previousForecast']=ref(old);f['revision']='WBS65-EXEC-FORECAST-95-USER_QUERY159_CURRENT_NORMAL';f['atJST']=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
for k,x in dict(low=.15,base=.4,high=.8).items():
 f['additionalCompletedWorkPp'][k]=round(f['additionalCompletedWorkPp'][k]+x,3)
 for n in ['additionalDiscoveredRemainingPp','revisedRemainingPp']:f[n][k]=round(f[n][k]-x,3)
tech=dict(kind='P01001_EXISTING17_CURRENT159_NORMAL_REQUEST100_FULL192_PARTIAL',evidence=ref(o/'manifest.json'),productTestsExecuted=159,newDefinitions=0,MainOrTestChanged=False,requestAllFour100=True,wholeScopeFour100=False,newAcceptance=0)
f['latestGroupTechnicalResult']=tech;f['remainingPriceAccountingNote']='Necessary changed dependency requal .15/.4/.8 only complete; originalP01001/2 unaccepted realDB/auth/replayfatal/coverage/endings. Tool helper2690 andhistorical roster2691 fixedwithin groupoverhead, no fee or productreexecution. Start label27051/usage1s deviation811 retained.'
fp=D/'820_WBS65予実・User照会一五九通常PT後版95.json';assert not fp.exists();write(fp,f)
audit=B/'evidence/PG27065-run-roster-schema-metadata-v1';assert not audit.exists();audit.mkdir();write(audit/'manifest.json',dict(actualExit=0,originalRows=31,originalTotals=totals,newActualRun=159,resultTotals=f['knownObservedProductRunTotals'],negativeControls=3,originalRowsRetained=True,productTestsReexecuted=0,wholeFormalUpdated=False,verifier=ref(Path(__file__).resolve())))
c=load(B/'input/1448_user_query_fatal_close.json');c.pop('sourceAfter',None)
c.update(groupId=load(B/'input/1449_user_query159_start.json')['groupId'],recordPath=str((D/'821_WBS65User照会一五九通常PT結果.json').relative_to(R)),manifestPath=str((o/'manifest.json').relative_to(R)),manifestSha256=sha(o/'manifest.json'),terminalAtUTC=v['atJST'],run=m['run'],workIds=['P01001-EXISTING17-CURRENT159-SOURCE_REQUAL'],outcome='GENUINE159_SUCCESS_REQUEST_FOUR100_FULL_REPOSITORY_ERROR_GAPS_RETAINED',technical=tech,forecastRef=ref(fp),nextCommand='Continue canonicalP01002 Usercommands actualown4 thenP01003 audit/token/replay; wholepublicsource/oracle andfixture admission. No159confirmation replay; actualTemp/Codec/KeyRing/DB/Root/native held. BUG beforefix andnecessaryPG preprice. Usage next16:30:54 actualclock.',checkpointText='固定source4a8cda433/Main eac757a58、27058全159真正0/FESabort0→27060 7d5d7d42独立0。全192物理/173positiveCRC、Request四100、全体L13M3C1B21未網羅Repository/QueryExceptionを除外せず表示。実DB/actual4/新defs/元190/正式更新0、正式1964-53/工数null。BUG2690元compile0回収/全helper3+47+6/negative3確認、BUG2691原31row schema保存/2647-2639-8→追加159=32run2806exec2798success8fail/negative3、両metadata限定close、製品再演0。群requal.15/.4/.8完了、版95残'+str(f['revisedRemainingPp'])+'未較正。原/2/native/451/17fatalruntimeOPEN、次P01002/usage16:30:54、通常区切り停止不可。')
write(B/'input/1456_user_query159_close.json',c)
for fn,text in [('915_障害表.md','BUG-2690:27055原producer/compile0→1452同compile回収、canonical3/protocol47/new6全hash、missing/extra/hash negative3、27056/27058全159/27060独立0。工具修正commit4a8cda433、CLOSED_LIMITED_METADATA。BUG-2691:27063原error→1455/27065原31全row保持・各exact1schema/独立合計とnegative3、metadata限定CLOSED、修正commit次公開へ、完了日2026-11-12。'),('916_横展開管理台帳.md','YKT-2367:canonical3(Inspectable含)/Protocol47/new6全物理hashとnegative3、compile回収のみ・製品再演0、4a8cda433、CLOSED_LIMITED_METADATA。YKT-2368:原31schema全行と追加159、独立2647/2639/8→2806/2798/8、missing/ambiguous/unknown negative3、27065 metadata0、全域/unique/formal/N-T値は更新せず、CLOSED_LIMITED_METADATA、2026-11-12。')]:
 p=R/'documents/900_OTHER/910_台帳'/fn;p.write_text(p.read_text()+'\n\n'+text+'\n')
p=R/'evidence/01_PT/010_NK-ADM-001/4089_P01001純値とJDBCinterface原十七件と現依存全一五九通常PT仕様.md';p.write_text(p.read_text()+'\n\n結果: source '+m['source']+' / Main '+m['productionCoreMain']+'、27058全159成功/FESabort0、[27060独立](../018_NK-OPS-001/evidence/PG27060-user-query159-independent-v1/manifest.json) hash7d5d7d425541f9c5101e3a33f1a5c9e7f65336503b992ae2658d42fb901cd4ce。192physical/173positiveCRC、Request全四100。全体L3817covered/13miss M808/3 C169/1 B1133/21、Repository/QueryException未網羅を除外せず保持。実DB/原/2/451/正式未受入、BUG2689runtimeOPEN、2690/2691はmetadata限定close。環境/command/exit/XML/hashはmanifest。\n')
for n in ['001_NK-ADM-001_単体テスト仕様書.md','002_NK-ADM-001_実行結果.md']:
 p=R/'evidence/01_PT/010_NK-ADM-001'/n;p.write_text(p.read_text()+'\n[4089通常PT](4089_P01001純値とJDBCinterface原十七件と現依存全一五九通常PT仕様.md): source4a8cda/Main eac、27058/27060全159成功/Request四100、全体L13M3C1B21未網羅保全、DB/原/2未受入。\n')
print(json.dumps(dict(manifest=ref(o/'manifest.json'),remaining=f['revisedRemainingPp'],roster=f['knownObservedProductRunTotals'])))
