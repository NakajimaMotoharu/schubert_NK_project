"""Freeze public read-wire defect, independent SDK fact and bounded PG price before edits."""
from pathlib import Path
import datetime,hashlib,json,re,subprocess
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';D=R/'documents/400_PGPT/470_PMO/600_通常PGPT_20261106'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));wr=lambda p,x:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
source='edaf641333266660ec79a6e070c98b7a79bbccac';base=R/'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/messaging';paths=[base/n for n in ['ProtectedReadWireClient.java','JmsRequestReplyException.java']]
assert all(p.read_bytes()==subprocess.check_output(['git','show',source+':'+str(p.relative_to(R))]) for p in paths)
assert (paths[0].read_text()).count('DateTimeException failure) {')==1
assert all('preserveFatal(' not in p.read_text() for p in paths)
ledger=R/'documents/900_OTHER/910_台帳/915_障害表.md';horizontal=ledger.with_name('916_横展開管理台帳.md')
assert max(map(int,re.findall(r'BUG-(\d+)',ledger.read_text())))==2720
assert max(map(int,re.findall(r'YKT-(\d+)',horizontal.read_text())))==2377
O=B/'evidence/PG27814-read-wire-catalog-before-v1';assert not O.exists();O.mkdir()
jms=R.parent/'toolchain/m2/repository/jakarta/jms/jakarta.jms-api/3.1.0/jakarta.jms-api-3.1.0.jar';assert sha(jms)=='6605e08075ab389c359451c7854808cf4b1575e1ea6317e534e9d4df088096df'
raw=subprocess.run([str(R.parent/'toolchain/jdk-25.0.4/bin/javap'),'-classpath',str(jms),'-c','jakarta.jms.JMSException'],capture_output=True,text=True,check=True).stdout
(O/'sdk-jms-exception-javap.txt').write_text(raw)
section=raw.split('public void setLinkedException(java.lang.Exception);',1)[1].split('}',1)[0];assert 'linkedException:Ljava/lang/Exception;' in section and 'initCause' not in section
v=dict(actualExit=0,source=source,inputHashes={str(p.relative_to(R)):sha(p) for p in paths},reviewedWholePublicSource=True,confirmedConversionSites=1,confirmedTotalSites=67,linkedExceptionCarrier=dict(sdkSha256=sha(jms),evidence=ref(O/'sdk-jms-exception-javap.txt'),setsCause=False),decision='Preserve fatal identity before the one outer UNAVAILABLE conversion, using module-local finite identity BFS cause/suppressed/SQL-next/JMS-linked edges. Clock/UUID/sender callbacks can supply these graphs. Keep pure generated codec conversion catches unchanged: closed typed value validation, no external provider callback. Do not alter SessionStoreException or SS333 compound priority. Existing finally wipe/cancel/release completes before outer conversion.',productTestsExecuted=0,newAcceptance=0,actualBrokerDbRootVmOperations=0)
wr(O/'before.json',v)
ledger.write_text(ledger.read_text()+'\n\n## BUG-2721（PG、2026-11-13、ProtectedReadWireClient.exchange外部callback例外graphの破棄、修正前）\n\n対象ProtectedReadWireClient.exchange外側UNAVAILABLE変換、JmsRequestReplyException、P01507/P016 UI232234235/SS311312321322323352/411§5。重要度高・優先高。期待UUID/Clock/senderが返すcause/suppressed/SQLnext/JMS-linked中のErrorを有限identity分類し同一Error伝播、非fatalは既固定UNAVAILABLE・秘匿を維持。実際六型catchが全graphを破棄。公開sourceレビューで確認、再現PTは未実施NOT_RUN。SDK JMSException.setLinkedExceptionはcauseを設定しない独立carrierであり既causeだけの分類では不足。原因固定catalog変換前の分類漏れ。影響共通一境界と四参照facade、timeout/送信数/registry/semaphore/wipe順変更なし。YKT2359既66+1=67限定site。修正前証跡018/evidence/PG27814-read-wire-catalog-before-v1/before.json。内部例外分類補足でRD/UI/SS外部仕様変更なし・QA不要。修正commit/再試験/完了日未確定、状態OPEN。\n')
horizontal.write_text(horizontal.read_text()+'\n\n### YKT-2359 BUG2721追加（2026-11-13、修正前）\n\nProtectedReadWireClient外側catch一つを追加し既66+1=67限定site。JMSExceptionの独立linkedException carrierも有限identity BFSへ含める。四facadeに共通し、純生成codec内catchは外部callbackなし/閉typed値検証のため非該当、JmsRequestReplyClientのExecutionExceptionは閉registryのtimeout/cancel由来で元cause保持、直接sender/clock例外はfinally cleanup後に外へ伝播する。SessionStoreException/ResourceScope等の異なる契約は変更しない。実broker/DB/VM/Root/actual4はHOLD維持。新helperと同一経路の通常PT完了後も他66siteを一括closeしない。\n')
price=dict(low=.075,base=.225,high=.45);old=D/'1080_WBS65予実・Log九class同一exec証明後版200.json'
if not old.exists():
 candidates=[p for p in D.glob('1080*.json')];assert len(candidates)==1;old=candidates[0]
f=json.loads(old.read_text());f.update(previousForecast=ref(old),revision='WBS65-EXEC-FORECAST-201-READ_WIRE_CATALOG_BEFORE',atJST=datetime.datetime.now().astimezone().isoformat())
for k,x in price.items():
 for field in ['additionalRequiredWorkGrossPp','additionalDiscoveredRemainingPp','revisedRemainingPp']:f[field][k]=round(f[field][k]+x,3)
f['additionalDiscovery'].append('BUG2721 one protected read callback conversion plus module-local finite JMS-linked classifier .075/.225/.45cap1; source/design audit .025/.075/.15 plus implementation .05/.15/.3. Later normal original32/new graph tests separately priced, no actual broker/Root/VM/DB or original acceptance credit.')
fp=D/'1081_WBS65予実・参照通信分類着手前版201.json';assert not fp.exists();wr(fp,f)
cfg=dict(groupId='PGPT-WBS65-READ_WIRE-CATALOG-ONE-SOURCE_ONLY-20261113',recordPath=str((D/'1082_WBS65参照通信分類PG開始.json').relative_to(R)),category='IMPLEMENTATION',kind='ADDITIONAL_FINDING',scope='BUG2721 local cause/suppressed/SQL-next/JMS-linked fatal graph classifier and one outer UNAVAILABLE guard; exact inverse/style only; no Test/runtime success implied.',oracleRefs=[ref(O/'before.json')],wbsLeafIds=['WBS-P015-07'],source=source,run='PG27816',estimate=price,capPp=1,workIds=['P01507-READ_WIRE-CATALOG_FATAL1-SOURCE_ONLY_PG'],forecastRef=ref(fp),nextCommand='Implement module-local finite JMS-linked graph helper and one outercall, retain cleanup/reasons, exact inverse/style. Pin source and independent join. Then price full current original fourwire32 plus independent graph tests after closure gate, no actual JMS/DB/Root/VM/held classes. ContinueP01615 after prior441 proof check.')
wr(B/'input/1826_read_wire_catalog_start.json',cfg)
print(json.dumps(dict(actualExit=0,before=ref(O/'before.json'),price=price,sites=67)))
