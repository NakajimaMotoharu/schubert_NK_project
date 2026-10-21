# 固定Caddy identity純粋Query単体仕様

WBS-P018-04.02、owner親P018-04（485のFixedServiceIdentity登録）固有のidentity fixture。RD SYS002/004/OPS・UI243/251/SS342§4 SSC178/181、既PGのresolveCaddy→resolveMaintenanceを点検する。origin/main ce7e3c7b5の承認設計を読取済み、設計変更不要。実NSS/kernel/current ownerの証明ではない。

開始event1615、群見積.05/.2/.6pp固定、原/v4不変更、共有/親/参照費の二重加算0。Mainはa03/e45不変更、Test-only新class FixedCaddyIdentityTestの三件。PT_DEFAULT、injected Queryへ公開literal byte配列を返すだけ、NSS/getent/process/VM/network/DB/鍵/Unit/権限変更を実行0、拒否cohort・不明安全条件への依存0。再送/並行は状態・資源を持たないquery adapterのため非該当（既nativeQuery実process契約の代用ではない）。

|TestID/method|入力・独立期待値|
|---|---|
|PT-CADDY-ID001/caddy001FixedAccountAndPrimaryOnlyUseExactlyTwoLiteralQueries|公開passwd caddy:x:997:993とgroup caddy:x:993、期待uid997/gid993/groups[993]、固定/usr/bin/getent passwd caddy→group caddyの二commandのみ。API/Web/config/read groupを問い合わせない|
|PT-CADDY-ID002/caddy002MissingMalformedAndMismatchedRecordsNeverProduceIdentity|空/別名/UID0/上限超え/複数行/primary不一致の独立literalを各fresh queryへ入力。全IOException固定service identity unavailable/causeなし/suppressed空、停止点でquery1又は2回|
|PT-CADDY-ID003/caddy003ProviderIoIsRedactedButRuntimeAndFatalAreNotDowngraded|first queryがsynthetic IO/RTE/Error、IOは固定診断へ変換、RTE/Errorは同一objectをthrowしidentityなし。query一回、実process取得0。query自体nullはconstructorの固定NPE契約も確認|

新classのみ追加、既全Test/oracle不変更。実装は既にprimary限定しており、本3試験/レビューで不一致がなければ不要なPG改変をしない。新6516は六module基準12/7＋新3/1=15/8、format→全testCompile→PT/static三phase。6518は原XML/851Main/1667class/六Jar/PMD raw1361/CS0を照合。新Testsourceのwhole/native/globalは未測定、全4064や先行20を加算/coverage合成しない。source/run/command/exit/hashは実行結果へ保存する。

事前確認21:45JST：新3宣言/15-8、wrapper三phase・reader全Main不変更・元資格hash/source/真正0を管理三件0で確認。初回管理は未commit新TestをHEAD差分に期待しguardが正しく拒否、実PT未発行。管理positiveは明示差分fixtureへ分離し、実source正当性はcommit後のguardで改めて確認する。未実行を成功に変換0。formatterは終了0、TestSHA `acfff67d55af530e890b083a7166928981e2bc51ed205cc4f27a4a9ad0f9d695`。Production PGレビューは固定account・primaryのみ/厳密field/ID上限/IO redaction/RTE-Error伝播、全source変更0。null Queryは取得前NPE契約、null出力は非null Query型契約違反で今回適用外、native admission/権限変更0。
