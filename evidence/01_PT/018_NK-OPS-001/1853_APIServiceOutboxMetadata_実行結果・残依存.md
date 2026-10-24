# API service/Outbox metadata PG/PT結果・残依存

2026-10-25/group2084/PG-D630/1852、branch dev-foundation、製品source73d94fc525c6ea8828ca82d906ec583146fee7bf未配備。API contextが既pool binding＋Outbox rows/age recorderをstrong保持し、既所有のimmutable Snapshotだけをrefreshで借用するPGを実施。実API callerは既resource scope/lifetimeのfactory/type供給だけ変更し、default source未供給を六NaNで明示。SQL/connection/worker/Clock/health決定権/業務再送/新external操作追加0。実RO source/producer/停止quiescence・nativeは別未完である。

## 実行済み/範囲

Linux/JDK25.0.4/Maven3.9.12、full PYTHONPATHは421/manifest。`python3 -B tools/quality/pg9028_api_service_six_compile.py` はoffline正常六build/Main-Test compile/NullAway/lint0・PT0。`pg9030_api_service_host.py` は新APISERVICE001～016＋APIMHTTP022/必要旧21＝actual38/2suite、F-E-S/aborted/notrun0。pool/config captureは初期化時各一回・metadata sourceはrender時だけ一回、STD未読、既SQL DAO/collectorの再実装・再実行0（fixture outerはcompile-only）。手書き3/5/7件・2/4/6秒と零/NaN、null/未知mode/primary Runtime-Error、pool取得失敗/close後未読、HTTP200/UTF8長/header/一回closeを独立literalで確認した。

9032の同source独立postは新binding＋既HTTP handler二MainがLINE60/METHOD10/CLASS2/BRANCH8の全missed0、PMD/Checkstyle/SpotBugs指摘0・processing0。各内訳はbinding L35/M7/C1/B4、handler L25/M3/C1/B4。JSpecify/NullAwayとnegative test、元source/classpath/XML/実exec append=false/CRC0/session1を結合し、7 receipt不正を拒否。scope以外・全module・全source四100へ広げない。

9031 caller staticのraw PMD2/exit4・全tool終了1はそのまま保持、CS/SB0。9033 v2で実source span/main-fatal、固定PMD7.28.0 jar規則、正式SS342/同source unitのdirect Java・非WAR/EARを個別照合し、J2EE container管理前提に限り非該当2/未分類0。4反例を拒否、抑制/実動作/全品質PASS/代替PT完了0。API start/close/所有・DB source・nativeのcoverageはUNRUN_HOLD/null。

9034 v3は全1,836 Main/追加binding一・変更ApiProcessMain一/旧1,834 byte不変、4 source差分を検証。factory/type置換を戻せばcaller業務本文/import集合/全literalが旧f690へ復元、旧HTTP21 Test本文も完全保持。metadata-only default/strong field/単一source読取/primary-finally/新I/O禁止の7改変を拒否。元235 source行のcanonical owner/costOwnerとchangeOwnerを分離しunknown0（P01809=215/C07=8/F02=4/C02=1/C06=1/P01805=2/P01806=3/C01=1）。485 current参照を更新し、原941 logical/歴史943 physical dataset・費用/元eventは不変更。現235のうち六つは元logical参照、新229候補であり新artifact受入を意味しない。

同source ArchUnit五規則も指摘0、bytecode importerのみで対象Main初期化0。実RO観測SQLは独立read-only transaction/READ_COMMITTED/1秒query timeoutを要求し、業務RW connectionへ流用しない。SDK refreshからI/Oせず、今後はSQL収集とSDK非依存のsnapshot cache/所有producerを分離して供給する内部依存を解消する。poll/close/再試行の実環境操作は今回行っていない。

## 工具是正（製品38/解析の再演0）

BUG1729/YKT1480：9033 v1未使用reのlint1後も親commandがtoolを続行したため、v1は未資格として保全。v2はimportだけ除去しlint0＋set -eで限定metadata資格。9035は合成正常0/期待lint停止1/壊れたgate対照73の3 controlと、元v1 lint1/新v2 lint0だけを実測。これは既拒否された処理の再試行ではなく、自作の非credential合成exit-only fixtureであり、実job/target実行0。以後の複数quality commandはfail closed。9028/30/32/31は元lint0で非該当、成功再演なし。限定CLOSED。

BUG1730/YKT1481：trace v1は実postにないaggregate字段を参照してKeyError1、v2は意図したtoken欠落のValueErrorをdriverが未受理で1。原script/元終了を保存（いずれもarchitecture子開始前）。shared selected_post_contractは実producerの全明示field/型/三static/四counter/CRC-session/除外flagsを検証し、9036の独立goldenと22不正を拒否。v3で正しい拒否型だけ受理し全trace/architectureを完了。旧8952/8938/8916は実unclassified/explicit staticを参照し非該当、再実行0。未公開owner legacy字段も原legacyReportedOwnerから継承し意味を保持。限定CLOSED、品質条件/期待値の緩和0。

## 主証跡（evidence/provisional配下）

|run|manifest SHA256|
|---|---|
|PG9028-api-service-six-compile-v1|370a39dc80cf8c1cd90997526b6377f1f68aa8b82c7c69b4a04b71c3e66d9f98|
|PG9030-api-service-host-v1|f316f20a1a040b8b50dd5ddb7c26cea5b9814973c8665d8d405cb649019c6333|
|PG9032-api-service-post-v1|4585f25047cd5f657152facf8486a44a69fe73c67d17345b864cd61e3965a358|
|PG9031-api-service-caller-static-v1|1dab5cae1970063d2cabbe329b45556ada50b53803fb1d1fd8aba2220d93c90e|
|PG9033-api-service-caller-context-v2|6eb3e7e243937e445a6f5411c78e432cbe0786c2b457b2c0caf744e3ef8a9f88|
|PG9034-api-service-trace-v3|caf310661eae47595a3b71f5472c052e4c6059e4e31ecdb3e5fead192aa17f4c|
|PG9035-preflight-fail-closed-v1|2db1cad80ed71eea4238ed81b5cfc966d32e9c884de676bf0bc7f97bbbaa3c99|
|PG9036-selected-post-guards-v1|e938bfec84234bc661860ac3b1060e7604c72c848a134ce826d361ca8a9cc7a6|

BEGIN/terminal・OS/JDK/tool/command/source/依存/入力hashは各manifest及びown PG379 slot、失敗traceはPG9034-api-service-trace-failed-v1/v2と原script。旧9033 v1は未資格/HISTORICAL_DO_NOT_EXECUTE、Tool unused lintの失敗をPASSにしない。source修正commit73d94fc52、工具/文書/証跡commitは当結果と同commit。own31131/43254/8379/97228終了0・7206 caller static1、全既結果を再起動0。実VM/DB/Root等の稼働状態は未照合HOLDのまま、操作0。

開始2/5/9pp cap10→共有51→52/reset1793382075（05:51観測、観測1ppは他chat内数/専有費null）。元計画のmetadata供給PG・新17PT、追加工具修正二件、source hash再認証を別記し、元/v4/v5を減額しない。token N/T/工数null、usageb36a4440。技術Java670ID/35Main（既653/34から＋17/1、異sourceの全体合算資格ではない）/config静的5と正式1964PT/53scope・原190新受入0を区別する。全C07/451/CHR/native・QA051final/PTALT0/G07未分類8,379/全actualHOLD維持、次公開scan/保存push後に許可されたsnapshot source分離へ継続する。
