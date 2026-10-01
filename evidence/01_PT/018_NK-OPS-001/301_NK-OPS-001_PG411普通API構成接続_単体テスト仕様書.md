# NK-OPS-001 PG411 普通API構成接続 PT仕様

## PG412追加・更新（2026-10-01、SSC150）

PG411時点の未実行欄を次で更新する。新Sourceの正式認定/100%は未達。

| Test ID | 対象・独立期待値/fixture | 実行結果 |
|---|---|---|
| PT-OPS-API-CFG-007 | ApiNonSecretConfig / independently written canonical text+JCA-SHA。literal59627、1/7/59627受理、空/0/-1/01/+1/小数/space/59628/長大/未知/共通側指定拒否。Production manifest自己件数からexpected生成0 | 新選択1成功、既存6も成功 |
| PT-OPS-API-KEY-006 | 既存shared fixtureの実credential reader/retainedFD、synthetic metadata/public65/66/67、閉じたcodecがcaller credentialを破壊せず目的/ctx1/fp1一致、closed credential拒否 | 新選択1成功、既存5成功 |
| PT-OPS-API-PREP-001～004 | ApiApplicationPreparation.execute/executeBorrowed、実ext4/保持FD、既存abc7file/hash固定Mediafixture、独立24literal登録。全usage/probe完了・immutableMap、31complete gateは不足拒否、期待件数1/6/8・不正owner/Transfermodeはcallback0、callback既知IO/未知runtime/fatalのidentity保持、borrowed root存続、publicnull全境界/partialmissingasset | 新4成功。native公的入口の成功/close fault/JCA欠如は未実行、合格0 |
| PT-AUT-LOGOUT-ASSEMBLY-001～003 | LogoutInboxServiceTest実PostgreSQL。factory初回0000/再送0200の280byte独立golden、非決定UUIDだけactual取得しversion4/異同検査、SQL Inbox/revoked/audit各1、fp1、null3、Caller鍵の再利用 | 新1成功、既存8成功 |
| PT-MED-ASSEMBLY-001～003 | MediaApplicationServiceTest既存med061公的graphをfactory経由へ変更。実DB/固定wire0000・ID・保存UTC、null5、後段各stage/fault/再送・8layout既存suiteoracle不変更 | 既存suite7成功、factoryへ新接続。新PT件数7を重複加算しない |
| PT-ADM-ASSEMBLY-001～003 | User Query/Mutation既存公的construct pathをfactoryへ変更。既存実PostgreSQL/golden/最新ADMIN/owner/inbox/session/audit/version後条件、各null4。生成UUIDだけ独立形式/変化を検査 | Query7/Mutation7成功、新接続で既存14を重複加算しない |

command：PG412選択v3、4module、verified12class、`spotless:apply test-compile jar:test-jar test spotbugs:check jacoco:report`、exit0/21:21:43。API52/依存各module成功・静的4zero。v1 private reader access失敗BUG418、v2 broad Exception close Werror失敗BUG419は別保存。Production/Source固定後のshared config/用途別鍵/所有/業務graph横断変更群が全6clean回帰trigger、途中helperごとの全回帰はしない。全回帰source/coverage/エビデンスhashは302へ固定する。

関連：RD AUT001～004/FIL001～009/MQ006～010、UI226/232/234/237/241/243、SS311/312/323/324/333/342/343、SSC148/149、BUG415/416/YKT330。

| Test ID | class/method・目的 | fixture/入力/操作 | 独立期待値・根拠 | 状態 |
|---|---|---|---|---|
| PT-JMS-DISPATCH-026-A～F | ApiSyncRequestDispatcher constructor/process・同期登録の完全性と借用 | UI232のLogin/同期/内部別context契約、SS323の要求31IDを試験側literalで列挙。欠落各31、余分response/internal、不明、null、例外identity、並行31、元Map変更 | 31のみ受理、他を開始前拒否。要求別の固定marker、delegateの同一例外、入力Map変更から独立。Productionから期待IDを生成しない | 選択6成功 |
| PT-OPS-API-KEY-001～005 | ApiNativeCodecs current用途別鍵・partial所有・消去 | 公開fixture32byte各65/66/67、ctx1/snp1/fp1。各読取位置IOException/null/31byte/非法version・3組reuse・fatal・close後 | copy全zero、借用codec closed、同一primary保持。HMACはSS324 LP byteをDataOutputStream/JCAで独立計算、固定owner7/LOGREQ01/001/REQUEST:LOGREQ01、AES metadataのliteralversionを照合 | 選択5成功、公的ServiceCredentialSet wrapperの実reader構成は追加PT必要 |
| PT-OPS-API-PREP-001～004 | ApiApplicationPreparation.execute 実root/probe/全usage/業務graph/借用期間 | 実Storage能力とcurrent credential、DB、時計、callback | probe→全usage成功後だけcallback。全close後借用不可。失敗時consumer無し/A保持、原本不変。人工呼出しでnativeRoot成功を代用しない | 未実行、合格0 |
| PT-AUT-LOGOUT-ASSEMBLY-001～003 | LogoutApplicationAssembly.create 既存認証/Inbox/再送graph | 用途別fixture鍵、実PostgreSQL/固定UTC時計、正常Logout/再送/null境界 | UI234固定電文、SQL session revoke/Inbox/audit各一度、別owner拒否、引数null拒否・caller鍵所有 | 新factory直接PT未実行、既存LogoutInbox8のみ成功 |

PG/PTは並行継続。本groupだけで全API/Web ready・native受入・全coverage100%・正式認定とはしない。正常/境界/異常/例外/null/並行/再送の未試験を合格へ加算しない。秘密・raw電文/session/keyはGit非格納。

実行：PG379/pg411-assembly-selected-v5.log。verified選択はMessageCodecTest/LinuxInodeSecurityTest/ServiceStartupAdmissionTest/ApiSyncRequestDispatcherTest/ApiNativeCodecsTest/ApiProcessMainTest/LogoutInboxServiceTest/TransferStoragePreparationTest、4module、spotless/test/spotbugs:check/jacoco:report、JDK25.0.4/Maven3.9.12/Node24.19.0/offlineM2。Sourceは0f9dc5925後の未認定変更群（保存commitから追跡）。選択coverageは既存exec累積を含むため正式coverageとして使わない。Source固定clean全6は変更security契約群を閉じてから行う。
