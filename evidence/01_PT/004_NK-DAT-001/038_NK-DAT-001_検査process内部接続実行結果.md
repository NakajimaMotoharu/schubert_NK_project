# NK-DAT-001 検査process内部接続 実行結果

2026-09-20 最新確定: 正式PT-WEB-20260920-26/source7df9eb2efbe929bf1fb498cf911f35d571285c5f、09:54:21～10:07:03 JST/Maven12:41/exit0、全1703PT（Protocol80/Storage82/API689/Web444/Batch367/CHR41）、failed/error/skipped0。6Java全line/method/class/branch100%、Production5 NullAway/Enforcer/Spotless/SpotBugs未解決0、固定path3method限定review継続・coverage除外追加なし、CHR SpotBugs未設定。JS1file全line/function/branch100%、18collector/41scope整合・79負canary成功。DB29/266＋Batch25/281＋OPS17/142＋QST2/16＋ASY1/5＋Web23/203＝97部分成果913PT（全1703の内数）、今回再開比+288PT/+32部分成果。PG212 Log結果8PT・PG213通信8PT・PG214入力8PTを限定認定、BUG224/225・YKT180/181・SSC073入力境界完了。PG215/216 Log画面状態/templateは仕様・草案のみ未加算。BUG195/206/YKT154/162/SSC063、実archive/親/質問受付全体/残Web・本文controller-file/readiness/Logout/QA045/実NKgateは未完了。固定加重40.85～52.35%（中心46.6%≒47%、約41～52%）を維持。残量12%で継続、元dev-web3file保全、PGPT/IT/ST未完了。以下は履歴。

037/PT-DB-INBOX-141～152、PG-D-135/SSC-049。探索3は2026-09-09 13:42:08 JST、33.905秒、dev-foundation/9843e921後の未commit実装、exit0。新12＋関連57=69件全成功、NullAway/Enforcer/Spotless PASS、SpotBugs0。新2classはline67/method8/class2/branch34/instruction383で全missed0。正式全体回帰・証跡確定までは未合格。Main/専用unit/親OS gateおよび全Program完了ではない。

Command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-api -am -Dtest=FieldCodecTest,OwnedTransferDirectoryTest,LinuxInodeSecurityTest,InspectorAesCredentialTest,InspectorCredentialAccessTest,InspectorCredentialLoaderTest,InspectorProcessTest test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check`。
作業log: /tmp/pgpt-inspector-process-explore-3.log。最初のnative生成testCompile誤りはBUG-101/YKT-090を先行起票。探索2の正系version17byte/Question必須token不足はBUG-102/103・YKT-091を先行起票してfixtureだけを修正した。2探索失敗を合格へ加えず正式再試験を待つ。

100同時呼出は1winner/99固定拒否・鍵4loadだけ。途中load/copy/時刻/DB失敗後と成功・WARNING・期限/割込の全終了で、sourceが渡した全materialのcopyKey拒否を観測した。Private copyは外部へ公開せず、OwnedKeys.closeの全array Arrays.fill→material closeと外側try-with-resourcesで全終了を覆うsource reviewを併用（private reflectionで消去を観測したとはしない）。途中codec公開/closeなし、閉じたmaterialを通常運用へ再使用しない。旧世代responseの独立JCE fixture1削除/SQL1-1-0-END、未知/QSB2行の暗号化body不変/SQL2-0-2-END、commit成否不明後の新instance再開でも二重削除なし。

YKT-090: 全native constructor検索の残りはstorage内のsymbol/fault port構築だけで正しいsignature。API/Webの公開利用はcreateであり変更不要。旧実native8/reader12 PTも探索3で成功。
YKT-091: 有効16byte literalに独立ASCII長assert、既存17byte拒否維持。QSBだけDB runtime UUID、GAMはNULL、Loginはtoken不要というV003制約へ整合。全12 PTはそれぞれの想定検査境界まで到達して成功。期待値をProductionから生成せずSQL制約/保護2件は変更しない。
