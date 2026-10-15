# PG3120～3128 全native Root-before・実Browser業務cohort仕様

## 範囲と受入境界

NK-OPS-001/NK-WEB-001/002、WBS-N14/N05/N06/N07/N08、CHR-A02参照。RD AUT/FUN/QST/NTF、UI223/224/225/226/236、SS313/314/323/331/332/343/355、QA048/049、DIF016。Production a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25/PG2802/BOM37bf、boot79a。Production Main変更なし。既全3691・native18の反復/再署名/再配備なし。正式1964/53・工数null・QA051 final保留は不変。

3104の当一回用zz-pg3100設定は既に準備済み。3106 actual0のpreparedAfter=f041e0b3318db88e7b94cd40a23d28ba7e630d405e1b13f9ae397f03a1312f24、nativeCanon=ab3fcad3e4f842562c7cd4cd77c5966b81ffba6534cf153c549cc1a5588aa4e2を接続する。旧UNKNOWN/prepare/Root/stopを再発行しない。

## 起動前純検査

`pg3122_prepared_browser_resume_contract_test.py` 3件actual0。全returned observer三fileと全Root-before payloadのpyflakes/compile、起動command唯一・durable guard先行、11項目postの厳密照合・新runtime・元parent保持・native16個の実byte保全・15/17/旧10拒否・元1800秒・同run限定resume（noargs/foreign/extra拒否）を独立literal/ASTで確認する。旧zz-pg2970は封印した前退役oracle内だけに残す。歴史的拒否/正当退役根拠まで新名へ書換えない。

最初の純組立でobserverの`__file__`基準directory不足を検出し実工具Rへ修正、VM操作0。初回count負例は埋込された旧退役oracleまで禁止する誤ったassertを検出し、当oracleが一個だけ残る検査へ修正。いずれも新工具のTDD/未実行準備であり、既稼働Production障害/正常化ではない。

## 実Browserの固定ケースと独立期待値

工具 `NativeNkBrowserBusinessCohort.java`。新cohortで一度だけ実施し、Root真正DONE/全24/全seal後も同ordinary API/Web/Caddy所有を保持。3つの独立Chromium contextはCurrentのdesktop/login driver、TLS検証有効・owned loopback SOCKSだけを使用する。Current lifecycle/reset/restartは呼ばない。

| Test ID | 入力/操作 | 独立期待値・根拠 |
|---|---|---|
| PT-NBR-001 | 保全済みactive credentialを0600/非symlink検査、READ ONLY SQL/JCA | ADMIN/ACTIVE/非lock、PBKDF2-HMAC-SHA256 salt16/310000/256bit一致。初期ADMIN発行/自己password resetを行わない。SS314 |
| PT-NBR-002 | 同userを3contextから順番にLogin | 毎回新auth session一個、Secure/HttpOnly/Lax。UI223のADMIN9card順/brand/username/role。固定列挙から期待値、Production呼出しで作らない |
| PT-NBR-003 | 新3sessionのDBと第一context保護GET | 第一新sessionだけREPLACED、第二第三有効、現在有効数2。第一context保護GETはLoginへ。DIF016/SS314 |
| PT-NBR-004 | 自己ADMIN詳細GET | HTTP200、username/ADMIN/4操作form、password/hash/role/status/version等の保護列不変。操作POSTなし |
| PT-NBR-005 | CSRFなし質問POST | HTTP403、業務質問作成なし。SS314 |
| PT-NBR-006 | form取得後同tokenで改行を含む質問POST | HTTP400、当tokenのquestions/更新Inbox0。本文のCR/LF禁止はUI224。JSに拒否されて未送信とせず実HTTP送信 |
| PT-NBR-007 | 固定 `PG3128 native 質問 <b>独立oracle</b>` を実DOM送信 | HTTP302→受付GET、受付ID26字・確認本文literal/子b要素0、owner+token質問一件・更新Inbox一件、locator三列のみ/同questionId。UI224/QA048 |
| PT-NBR-008 | 保持した同token/同本文を実HTTP再送 | HTTP302・同receipt、質問/更新Inbox全行不変。新token/質問/結果の捏造なし。QA049 |
| PT-NBR-009 | 受付GET refresh | HTTP200/同本文、質問/更新Inbox不増。QA048/049 |
| PT-NBR-010 | 通知一覧GET | HTTP200/当receipt一行、当question+owner通知一件。処理stateは競合可能なのでCOMPLETED固定など未承認の期待値を追加しない |
| PT-NBR-011 | 第二第三contextの正規Logout | 二新sessionがLOGOUT失効、管理resetなし。第一のREPLACEDをLOGOUTへ上書きしない |
| PT-NBR-012 | 読取SQL/実info再確認 | 保護account列不変、当新question以外の既questions/answers/jobs/notifications全列不変、同a9/schema028/info五field。全24/所有/資源sealは外側で別必須 |

全予定ケースは未実行。部分PASSやこのcohortだけをCHR全体/四coverage100/正式451/IT/ST合格にしない。失敗した場合は既発行POSTを盲目的再送せず、safe case記録と独立SQLから状態を確定して915/916へ先行起票する。

## 現在の工具検証

Java25.0.4 `javac -Xlint:all -Werror` 実0。CurrentCharacterizationTest/NativeNkBootstrapAuthenticationは共有driver/JCA純methodだけを新-only class directoryへcompileし、後者mainは実行しない。初回compileは古い460 class ABIとAPIResponse非AutoCloseableを検出、実sourceの同driver compileと明示disposeへ修正、VM操作0。

`NativeNkBrowserBusinessOracleTest` 実0：型付きinfo20vector、保護account4、session欠落/重複/未知3負例、SQLquote、固定HTML本文。network/credential/DB read0。

`preflight` 実0（exec62154）：boot79a・morning/API/Web/Caddy MainPID/ControlPID/Job0・当zz3100存在をfresh RO照合後、保全済み専用credentialと実DB/JCAを再認証。password/鍵/token/cookie/session ID/hash実体を標準出力/Gitへ保存しない。私有`PG379/pg3128-browser-credential-preflight-v1/PT-NBR-001.safe.json`。この結果はまだBrowser/Root成功ではない。

## 残る発行前条件

実行wrapperの当genuine terminal/fullseal/ordinary tuple/SOCKS before-after照合、全24の追加業務許可差分oracleと新seal、実Java class/input hash封印、new-only observer stage/watchと初期quiescence。これらが揃う前は3122 Rootを発行しない。Root後は実Browser全予定ケース→許可差分/新seal→最後に正規ownedstop/独立post/nativeを実施する。

ログ/manifestは新-only私有0600、公開はcase結果・件数・hashだけ。SQLはREPEATABLE READ READ ONLY、statement5秒/lock500ms、全24読取64MiB上限。既存方針に従い一貫した全24before/afterとowner/計測窓だけはnew-only私有0700/0600へ保存し、DB/password hash/token/session実体をGit/公開manifest/標準出力へ出さない。raw password/cookieは保存せず、例外全文/Playwright requestbody/DOM/screenshotは出力しない。

3136の独立全24 oracleは、十master/保守表とpending revoke不変、保護account列/他account不変、既存全行保持（当owner旧authのREPLACED三列だけを限定）、新質問一/新job一/新通知一・FK/owner/state、locator三列/UTC millisecond、fresh auth三のREPLACED一＋LOGOUT二、Login Inbox三/質問更新一/Logout二または失効coordinationを含む三、実QWKREQ01一件SENT、Logout後匿名Web三、実Web log/outbox一対一SENTを検査する。無根拠な表単位allowlistだけでは通さない。新回答provider結果の意味は当cohortの受入外であり、別の回答契約/CHRを閉鎖しない。純三試験（正常二経路/禁止差15/既行破壊三）実0。

3130/3132/3134は新activation・実3122開始時刻・同run/cutoff・preparedAfterへ全terminal/全24/全seal consumerを接続する。旧10項目snapshotへのnative投影を廃し、当11項目のnativeCanonと保全16実fileをそのまま照合する。純二試験0、両旧activation拒否/完成namespace/非mutation/元before hash/16個/新観測窓を検査。完成sealに終端出力slotは含めないため、純試験では終端GUARD内の新activationを照合する（未実行の証跡path存在を要求しない）。

3138はclean sourceからshared Current driver/JCA/新工具を-Xlint:all-Werrorでnew-only classへ封印し、純oracle/三Python suite/当credential ROを全実行してhash固定する。3122はこれを必須gateとする。3140は新3134/3130の真正証跡・同四ordinary owner/SOCKSを前後で保持して実Browser→readonly最大90秒Log配送観測→別3136全24を実行する。600秒はこの有限Browser工具の上限であり、Root1800秒/業務DB/MQ/Unit期限は延長しない。Root/Browser/stopは現時点未発行。
