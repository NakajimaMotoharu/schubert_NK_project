# 082 NK-WEB-002 User業務接続実行結果

## 同User変更群fresh全体受入（six-full-v2、15:15:11）

source `5e2afd8911fcb19266d05b62461a62b1da297fc8`、dev-foundation、WorkPG379 pg452_full_v2.shによる全6 fresh clean/format/compile null-Werror/test/static/JaCoCo/JAR/runtime採取、actual0/17:17。3171PT465suite/F/E/S0（protocol81/storage154/bootstrap213/API892/Web809/Batch1022）、SpotBugs6module0。全sourcefiles検査一致/全6actualtarget byteをWorkPG379/pg452-hostへ捕捉し、既存collectorの13User対象・32所有対象・11Content対象全miss0を確認した。新User対象13はB298/L733/M119/C13各miss0、除外追加0。LOCKED解除0000/version1→同token保存0200/version1・解除監査1/Inbox再送1/資源数値0を同sourceで初めて完走。先行v5や不合格v1を補完しない。

安全全体manifest: `../018_NK-OPS-001/evidence/provisional/PG452-user-business-full/manifest.json`、SHA256 `220dbdef65d409343a1c8181b8d0b63ff484da49a5fb8254f432e03f18acf7a3`。XMLはsuite/testcase属性だけ、provider/properties/stdout/stderr/raw電文/DB/session/credentialは含めない。BUG639640修正3c2466b41、BUG641～644修正1528835cf、BUG645修正5e2afd891、各before/独立再試験/対応YKT452～457を同全体へ結びhost対象範囲を完了する。全体host未網羅はB1222/L3477/M567/C39でnative起動等が残るため、全coverage100や正式run24の更新にはしない。次同起動経路の通知取消・質問削除→native全業務/同owner/Caddy/DONE/CHRへ継続。

## six-full-v1 不合格（14:54:06）

source1528835cf6fd11d9003ead436003e5977749c660、actual1、protocol81/storage154/bootstrap213/API892成功、Web809試行1F/E/S0、合計2149試行/1F。Batch/Web static・reportは未実行なので古いv5 targetを補完しない。sourcefiles一致/実5byte WorkPG379/pg452-six-full-v1-frozen、log SHA256 `f22371d655ce5b6c11a65571bf1a2053dadb482e0116a633238b5da30c15825e`。追加BIZ010 LOCKED解除0000/version1→保存再送0200/version1/failed_count0/locked_untilNULL/監査1/Inbox再送1の後条件まで通過したが、最後の資源assertでInteger0とAtomicInteger本体を比較して失敗（BUG645/YKT457）。修正前起票・全byte捕捉後に数値getだけ是正。業務後条件や先行v5を全体成功へ流用しない。次sourceを固定してfresh全6 v2を実行する。

## user-http-selected-v5 限定接続合格（14:31:42終了、全体/native未受入）

source3c2466b41af997ca3534436bba055d86ad7d18f6＋PG-D366/367 dirty、actual0/242PT24suite/F/E/S0、protocol5/storage7/bootstrap10/API59/Web118/Batch43、SpotBugs6module0/NullAway-Werror成功。sourcefiles全一致、全6actualtargetをWorkPG379/pg452-user-http-selected-v5-frozenに捕捉済み。安全manifest `evidence/provisional/PG452-user-http-selected-v5/manifest.json` SHA256 `ced7cf1409c98cae70e611afeb53829e3974478f95ad22bb565d99865a2d3738`。log `e54f3bcd03a136000957d5529b80f9368b550ab47abc1552e2cfa211009340ab`、sourcefiles `7849c09e76f7c7b01822636c2e7f6ce766ba55b2f2951d349352b6920d1ea2c3`。実行前src/tools全byteのprivate archive SHA256 `cb6a8541c14b317f7a4ea35e862360328266693a0609b0d4299dfac1357a9844`（0600・Gitへ保存しない）。捕捉後の追加LOCKED解除再送method/collectorはこの成功sourceへ含めない。

User接続13 executable classはline/method/class/branch全miss0（Controller B124/L295/M18/C1、API UserQueryRepository B52/L130/M18/C1、全counterはmanifest）。実HTTP same-coreログイン→新User作成→自己PASSWORD→302/login/Max-Age0/暗号local row0/業務auth revoke1、自己SECURITY監査1/架空SESSION_EXPIRED・追加LGO0。真正APIではversion0→詳細→STATUS1/同token保存再送1/別input409、ROLE2/両category監査各1、UNLOCK既解除0200同版2、他UserPASSWORD3を確認。100並行同tokenは全302/version1/Inbox再送99、送信thread local TX0/全future後global0。TIME001は五μsDB原値不変と独立ms固定wire、負/null/failure/capacity/unknown全観点を含む。hostのJMS transport fixtureでありArtemis/native/Web親ready/CHR/全体正式は未完了。

### v4不合格を保全（14:21:54）

actual1、Web118試行2F/E/S0、Batch/Web静的未実行。BIZ009真正HTTP自己終端は成功したが2監査集計期待は不合格、全合格へ流用0。実5byte WorkPG379/pg452-user-http-selected-v4-frozen、log `0b5bc3dc810e4e4d58f21f8cba2176c70e81125322844243f20b4460c465d340`。BUG644原仮説「過去監査混入」は初期化後も2で不成立、SS351§5は作成/STATUS/ROLEのACTIONとSECURITYを各1保存する。誤aggregate1 oracleを独立category別SQL各1/target/successへ訂正（Production監査・上位oracle不変更）、YKT456対象3SQL＋Role/Password/Unlockを確認しv5成功。fresh全体・修正commitまで未閉鎖。

### user-http-selected-v3 不合格（14:14:27）

actual1、API59（UserQueryRepository8含む）まで成功、Web115試行3F/0E/0S、Batch/Web static・coverage report未実行。全sourcefiles一致/実5byteWorkPG379/pg452-user-http-selected-v3-frozen、log SHA256 `e27f11f0a9fcc2921a8689ab967ff30e5930387d2994b2c62b7c1699ec0f3340`。BUG641は独立TIME001五μs原値/固定ms wire＋UserQueryRepository B52/L130/M18/C1全miss0、真正API BIZ010作成0/詳細0/更新1/同token再送1まで到達したが後続監査assertで停止。BIZ011100futureは302/実version1まで到達し送信thread local TX0の反例は解消したが監査成功count1期待/2実で停止（BUG644）。BIZ009は/login cookieへ到達、plain TOKENをDOMと誤読して空CSRF/Login403（BUG642未閉鎖）。部分到達をBIZ010/011全合格や3F補完へ使わず、BUG644/YKT456修正前登録後にfixture隔離/入口body契約を是正してv4へ進む。Production audit期待値/CSRF/DB原値・wirestrictは不変更。

### user-http-selected-v2 中断ではなく不合格（14:02:53）

actual1、protocol5/storage7/bootstrap10/API51成功、Web115試行0F/3E/0S、Batch/Web静的・coverage report未実行。sourcefiles全一致、実5target WorkPG379/pg452-user-http-selected-v2-frozen、private log SHA256 `0c26031e2aa8c7669e03db7780201d4b1941bdbaf13928e3332488b29f1cac5d`。BIZ010作成version0後UDTのsub-ms未投影（BUG641）、BIZ009menuMvcで未mappingの/fixture cookie不在（BUG642）、BIZ011他thread稼働を送信thread所有と誤判定（BUG643）。source3c246＋dirtyを保全して修正前台帳登録、失敗runへ後続成功を補完せず、未到達の全User往復/100/self-resetを合格へ加算0。

PG-D366/SSC177/081・057、2026-10-04。token群と正規Version0の先行接続だけであり、全User HTTP/native/正式認定は未完了。

## 同User HTTP先行観点・未受入（13:51終了）

HEAD3c2466b41af997ca3534436bba055d86ad7d18f6＋User full3arg/画面/terminal及び新独立6PTのdirty source。`pg452_selected.sh user-http-selected-v1` exact23class（全6canary含む）はactual0/223PT23suite/F/E/S0/static6module0/compile null-Werror成功。内訳protocol5/storage7/bootstrap10/API51/Web107/Batch43。BIZ001/002/003/004/005/009の先行6methodは372/60/68/324/60 byte、実表示token数/容量、fresh競合UDT/同token、実MVC DOMの確認に限定する。

source-files SHA256 `7159e37234b79973117ae05ef6440701e900ac88e0f5b24f01aad36a61fb985a`は全検査一致、log SHA256 `8c6fc2c6f3c5bb5387e7aa888e7984f1eb9b97f700938feba5fe7a8eab84b1db`、全6actualtargetはWorkPG379/pg452-user-http-selected-v1-frozenへ別保存済み。raw private log/電文/DBをGitへ混入しない。Controller残B30/L53/M1/C0、CreateView残B2/L4/M1/C0、ApiInvalid残B9/L2/M1/C0、BusinessConfig全4counter0であり、本先行選択を100%や全機能合格へ加算しない。次は同群の真正API create0/detail/update1/0200・実Security same-core HTTP/self UPW、100同token競合、全非成功/保存失敗/null/fatalを追加し、source固定選択を行う。全User機能受入/同群fresh全6/native/CHR/正式は未完了。

## 先行selected-v1

source HEAD1034d60a329a4f1c0f4d7e20480408ce29e124db＋PG-D366 dirty、dev-foundation。WorkPG379 pg452_selected.sh user-selected-v1 exact22classの全6reactor。actual0/03:57/13:20:40 JST終了、217PT22suite/F/E/S0、静的6module0/NullAway/-Werror成功。protocol5/storage7/bootstrap10/API51/Web101/Batch43、TOKV209A～E・DETAIL009全成功、既存単件TOKV207208/4form/current encrypted session/security/User/APIも選択回帰。

対象4class（SessionOperationTokenLifecycle/SessionOperationToken/UserDetailViewModel/UserAdminController）はB68/L206/M33/C4各miss0、除外追加0。44容量subcase・最古完成/同時刻保存順・旧及び今回UUID衝突/commit-close不明の実row再読・8thread100組の5成功95拒否/10token/10UUID/資源0、正規UDT320 Version0/maxの表示を独立固定List/SQL/byte/Clockで確認した。NPE catch正常化0。sourcefiles一致、全6actualtarget byteWorkPG379/pg452-user-selected-v1-frozen、安全manifest `evidence/provisional/PG452-user-selected-v1/manifest.json` SHA256 `fe849db35d959371e4c3fe8410568241f25fe469856e3b215c5cbf71db6ccda0`。

## before・残る受入

user-before-v1 actual1/13:13:45、前段73PT成功/Web101試行1F2E、Batch/Web static未実行。DETAIL009の独立正常期待に対し旧guardはnull/503（BUG639）。固定Fixtureを反復した209A/Cは残rowで衝突（BUG640/YKT453）。実5target/hash/log d3d59bec…をWorkPG379/pg452-user-before-v1-frozenへ保存し、結果/旧誤oracle成功を新正常合格へ流用しない。

是正はtyped N9既存0～maxに余分なpositive guardをかけないこと、旧005/057の誤version0異常を009正常へ戻すこと、各独立fixture subcaseへ既存resetを明示することだけ。Production UUID/unique制約は緩めない。BUG639/YKT452は新User追加→詳細→初回変更のHTTP/実API結果・同群fresh全6まで未完了、BUG640/YKT453も同群full確認/修正commitを対応する。今回collectorは凍結後追加で全source gate未達。次は同coreをUser full GET/5POSTと自己reset local終端へ結線、対象4coverage/static/source固定fresh全6、続く取消/削除・native全Ready/Caddy/DONE/実CHR/全scope正式へ進む。正式run24/source858713c0/1964PT53scope不変更、raw credential/session/cookie/token/key/DB dump/log/provider出力はGitへ保存しない。
