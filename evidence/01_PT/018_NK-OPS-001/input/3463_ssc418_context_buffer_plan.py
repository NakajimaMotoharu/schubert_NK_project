"""Plan the same-path buffer ownership repair, publishing internal SS before source edits."""
from pathlib import Path
from decimal import Decimal
import hashlib
import json
import subprocess
import difflib

root=Path.cwd();base=root/'evidence/01_PT/018_NK-OPS-001';inp=base/'input';docs=root/'documents/400_PGPT/470_PMO/600_通常PGPT_20261106'
load=lambda path:json.loads(path.read_text());sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest();write=lambda path,value:path.open('x').write(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();main=subprocess.check_output(['git','rev-parse','origin/main'],text=True).strip();source='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/messaging/ProtectedReadWireClient.java'
cost_new=dict(low=.4,base=1.2,high=2.4);carry=dict(low=.2,base=.6,high=1.8);total=dict(low=.6,base=1.8,high=4.2);gid='PGPT-WBS65-SSC418-CONTEXT-BUFFER-OWNERSHIP-20261115'
detail='''ProtectedReadWireClientの既6引数package-private構築口と全public facade APIを維持し、defaultはprivate stateless JDK操作実装に固定する。ASCII変換はAuthenticationContext.wireValueからUS_ASCIIの新規64byte、比較は既MessageDigest.isEqualでありalgorithm/認証/権限/電文/画面/再送/期限/queueを変更しない。外部設定・HTTP選択・動的loadingで切替えない。新しい7引数package-private口は内部ContextOperations（encodeとsameの二操作）を受け、operations nullをconstructorの明示nonnull preconditionで拒否する。標準実装は状態/credentialを保持しないprivate static final class、操作interfaceはpackage-privateでbinary Code0を実証し除外としない。

encodeの戻りはnullable boundaryとして宣言し、contextBytesがnull又は64以外を固定IllegalStateExceptionで拒否する。nullは未取得、非null返却時にownedとなる。長さ不正の返却bufferはhelper自身が消去してから失敗し、呼出側へ返した正規bufferだけが次の所有へ移る。第一bufferを取得した直後に外側try/finallyへ入り、その中で第二を取得して内側try/finallyへ入る。第二の取得/検査に失敗すれば取得済み第一だけを消去、比較失敗なら第二→第一をそれぞれ一回消去する。JDK内部の返却前の未到達allocationまでを消去保証したと主張しない。実OOM/Thread操作/JDK差替えで故障を誘発しない。

decodeはinstance内でこの既owned比較を使う。既catalog catchの固定INVALID_RESPONSEは保持し、変換前に既JmsRequestReplyException.preserveFatalでcause/suppressed/SQLnext/JMSlinkedのError identityを保存する。新package-private口の非fatal/不正結果だけが従来の閉分類へ落ち、Errorを通常結果へ変換しない。Root/VM/DB/SDKbackend/actual4/Root2/拒否fixtureへの代替口ではなく、元から許可された同memory-only componentの例外消去を検証する。public synthetic contextだけを用い、実token・session・鍵・原本にアクセスしない。

PTは既58全本文/独立wire/golden/timeout/並行/secret-wipeを保持し、新whole ProtectedReadContextOwnershipTestの6methodを追加する。CONTEXT001 first/second/compareの合成Errorで取得済み全buffer消去とError同一、002比較RTE内Errorの同一伝播、003通常RTEの固定INVALID_RESPONSE/消去/秘匿、004null operationsの構築前拒否、005null encode第一/第二で既取得分消去と固定分類、006不正幅0/63/65を第一/第二で与え返却済み全bufferの消去と後続comparison0。正常/不一致のdefault JDK動作・全8旧クラスは既58で再資格し、必要な同source whole64・全physical195等を推測せず新compile実物から確定する。new6と旧58を区別し、old58成功を新sourceへ流用しない。

原58群の未達carry.2/.6/1.8ppを保持し、新Source製造/SS補足/六PT分だけ.4/1.2/2.4pp追加、当群合計.6/1.8/4.2pp cap6。元群.8/2.4/7.2/cap8・元P005費・元904.85/SV各上限は不変更、carryを二重追加しない。新13Mainは変更sourceなのでRoot compiler/NullAwayでfresh compile、全9wholeTestと静的、同一64execのdefault及びunfiltered全命令/行/メソッド/クラス/分岐、CRC/init/sourceを確認する。各naturalB0/Code0は明示、全Protocol依存を含む全物理scopeの未達を保存しown/source/全194等を混同しない。global451/正式/工数/CHR/native/ITSTを受入にしない。'''
detail=detail.replace('全physical195等','全physical数等')
plan=dict(groupId=gid,source=head,productionCoreMainBefore='fb1783d3dfb1a2e850b81be50ec26b3949ccc398',scope=detail,ssc='SSC418',bugs=['BUG3012','BUG3013'],horizontal=['YKT2541','YKT2542'],sourcePath=source,sourceSha256Before=sha(root/source),newBudgetOnly=cost_new,carriedExistingBudget=carry,estimate=total,capPp=6,newTestDefinitions=6,necessaryPriorDefinitions=58,expectedTests=64,physicalExpected=None,methodCountsExpected=None,newMainFiles=0,mainSourcesModified=1,newScopeOrQualityRelaxation=False)
pp=inp/'3464_ssc418_context_buffer_plan.json';write(pp,plan)
previous=next(docs.glob('2115*'));forecast=load(previous);forecast.update(revision='616-SSC418_CONTEXT_OWNERSHIP_NEW_SOURCE_WITH_ORIGINAL_CARRY',previousForecast=dict(path=str(previous.relative_to(root)),sha256=sha(previous)),latestAdditionalFinding=dict(workId='P00502_SSC418_CONTEXT_BUFFER_OWNERSHIP',newBudgetOnly=cost_new,originalCarry=carry,groupEstimate=total,reason='Actual raw9I/1L and first-buffer acquisition-before-try source defect; close same connection path with internal trusted operations, not held Root substitute.'))
for key,value in cost_new.items():
    for field in ['additionalRequiredWorkGrossPp','additionalDiscoveredRemainingPp','revisedRemainingPp']:forecast[field][key]=float(Decimal(str(forecast[field][key]))+Decimal(str(value)))
forecast['currentFullForecastBudgetBridge']['additionalRemainingPp']=forecast['additionalDiscoveredRemainingPp'];forecast['ssc418CarryBoundary']=dict(groupEstimate=total,oldRetainedUncompletedCarry=carry,newGrossAddedOnly=cost_new,carryRecharged=False,original58GroupEstimateFrozen=True)
fp=docs/'2117_WBS65予実・SSC418所有補足carry版616.json';write(fp,forecast)
paths=['documents/300_SS/310_アプリケーション/311_モジュール・package・class責務設計.md','documents/300_SS/350_運用・品質/352_Security・credential・監査実装設計.md','documents/900_OTHER/910_台帳/914_詳細設計修正管理台帳.md']
patches=[]
for path in paths:
    upstream=subprocess.check_output(['git','show',main+':'+path],text=True);local=(root/path).read_text();marker='## SSC-418 '
    assert marker not in upstream and marker not in local
    section='\n\n## SSC-418 保護読取の一時context buffer所有・例外消去（2026-11-15）\n\n'+(detail if not path.endswith('台帳.md') else 'BUG3012/YKT2541 raw finally9I1L不足、BUG3013/YKT2542第二取得前保護域不足をSS311/352内部所有/testability補足として是正する。'+detail+'\n\n状態: 設計確定・main反映前、PG/通常PT/全PGPT未完。')+'\n'
    target=upstream.rstrip()+section;(root/path).write_text(local.rstrip()+section)
    patches.append(''.join(difflib.unified_diff(upstream.splitlines(True),target.splitlines(True),fromfile='a/'+path,tofile='b/'+path)))
evidence=base/'evidence/PG33740-ssc418-context-buffer-design-only-v1';assert not evidence.exists();evidence.mkdir();patch=''.join(patches);write(evidence/'design-only-main-patch.json',dict(baseMain=main,paths=paths,patch=patch,patchUtf8Sha256=hashlib.sha256(patch.encode()).hexdigest(),source=head,implementationIncluded=False))
spec=base/'4275_SSC418_context一時buffer所有・例外PT仕様.md';spec.open('x').write('# SSC418 context buffer取得直後保護・独立単体仕様\n\nRD AUT/MQ/TST、UI232234235、SS311323352、BUG3012/3013・YKT2541/2542、WBS-P005-02・関連F03/P01607/10/13/14。\n\n'+detail+'\n\n新入力は独立UI232のoffset0/8/11/19/22/23/24/60/96/113/177/181/187/193/199/208を使う272byte ANMRSP01成功・16byte空menu（全count0/flag0/reserved spaces）の手書きvector。expectedはfixedASCII64/zero配列/明示call数/同一Error/固定reasonでありProduction codec/比較/消去methodで生成しない。返却bufferと旧caller-owned contextは区別し元String/入力contextの再認証やsecret解決をしない。null operationsはnonnull構築契約の明示拒否でNPEを正常処理としてcatchしない。encoder null/不正幅は固定失敗で偶発NPEを排除する。negative actualprovider/VM/Rootは一切起動しない。\n')
config=dict(groupId=gid,recordPath='documents/400_PGPT/470_PMO/600_通常PGPT_20261106/2118_WBS65SSC418取得直後保護開始.json',category='IMPLEMENTATION',kind='ADDITIONAL_FINDING',scope=detail,oracleRefs=[dict(path=str(pp.relative_to(root)),sha256=sha(pp)),dict(path=str(spec.relative_to(root)),sha256=sha(spec))],wbsLeafIds=['WBS-P005-02'],implementationArtifactPaths=[source],source=head,run='PG33748-SSC418-CONTEXT-OWNERSHIP-WHOLE64',estimate=total,capPp=6,workIds=['P00502_SSC418_CONTEXT_BUFFER_OWNERSHIP'],forecastRef=dict(path=str(fp.relative_to(root)),sha256=sha(fp)),nextCommand='PublishSSC418SS311352914ONLYmain via ordinaryPR beforePG. Implement same private context path nested immediate ownership/nonnull64 factory/defaultJDK operations+finitefatal guard, newwholeContext6+existing58=64. Preserve residualcarry and originalbudgets, no fakeRoot/refusal/actualOOM/key/SDKbackend/Root2/Actual4/VM/native/DB/aru. Freshquota/hourly; ordinary group not stop.')
write(inp/'3465_ssc418_context_start.json',config);print(json.dumps(dict(actualExit=0,ssc=418,newBudgetOnly=cost_new,retainedCarry=carry,total=total,expectedTests=64,designBeforePG=True)))
