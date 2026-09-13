# NK-DAT-001 検査process内部接続 実行結果

2026-09-13 最新確定: dev-foundation/source b234a4b356a9b456d3fdd245dbd6baed568be426、正式PT-WEB-20260913-14（10:51:57～11:08:12 JST）、全1415件（Protocol80/Storage66/API660/Web241/Batch327/CHR41）PASS、failed/error/skipped0。実装済み6 Java moduleのline/method/class/branch100%、Production5 moduleのNullAway/Enforcer/Spotless/SpotBugs未解決0。固定/etc・/run・/varの3 method限定静的レビューを維持しcoverage除外なし、CHR runnerのSpotBugsは未設定。15collector/38scopeの同run/source/branch/hashと41負canary成功。DB29部品266＋batch22部品241＋OPS14部品118＝65部分成果625 PT（全1415の内数）。PG171～174のfile/root namespace/Systemctl/NSS終了処理の306compoundを正式再確認（新JUnit/部品加算0）。BUG198/YKT157完了、BUG195/YKT154/SSC063はSQL等の広域残候補があるため継続。root manifest生成/実dump・tar・age/7世代・親実子制御/全cleanup接続/通常Question writer/replay/Logout RERUN001/QA045は残る。固定加重約4割（35～50%、456）を維持、再開比+304 PT/+30部分成果。実NK CHR/IT/ST完了とはしない。利用枠残10%のため新規実装を停止し保存中、元dev-web3file保全。以下は履歴。

037/PT-DB-INBOX-141～152、PG-D-135/SSC-049。探索3は2026-09-09 13:42:08 JST、33.905秒、dev-foundation/9843e921後の未commit実装、exit0。新12＋関連57=69件全成功、NullAway/Enforcer/Spotless PASS、SpotBugs0。新2classはline67/method8/class2/branch34/instruction383で全missed0。正式全体回帰・証跡確定までは未合格。Main/専用unit/親OS gateおよび全Program完了ではない。

Command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-api -am -Dtest=FieldCodecTest,OwnedTransferDirectoryTest,LinuxInodeSecurityTest,InspectorAesCredentialTest,InspectorCredentialAccessTest,InspectorCredentialLoaderTest,InspectorProcessTest test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check`。
作業log: /tmp/pgpt-inspector-process-explore-3.log。最初のnative生成testCompile誤りはBUG-101/YKT-090を先行起票。探索2の正系version17byte/Question必須token不足はBUG-102/103・YKT-091を先行起票してfixtureだけを修正した。2探索失敗を合格へ加えず正式再試験を待つ。

100同時呼出は1winner/99固定拒否・鍵4loadだけ。途中load/copy/時刻/DB失敗後と成功・WARNING・期限/割込の全終了で、sourceが渡した全materialのcopyKey拒否を観測した。Private copyは外部へ公開せず、OwnedKeys.closeの全array Arrays.fill→material closeと外側try-with-resourcesで全終了を覆うsource reviewを併用（private reflectionで消去を観測したとはしない）。途中codec公開/closeなし、閉じたmaterialを通常運用へ再使用しない。旧世代responseの独立JCE fixture1削除/SQL1-1-0-END、未知/QSB2行の暗号化body不変/SQL2-0-2-END、commit成否不明後の新instance再開でも二重削除なし。

YKT-090: 全native constructor検索の残りはstorage内のsymbol/fault port構築だけで正しいsignature。API/Webの公開利用はcreateであり変更不要。旧実native8/reader12 PTも探索3で成功。
YKT-091: 有効16byte literalに独立ASCII長assert、既存17byte拒否維持。QSBだけDB runtime UUID、GAMはNULL、Loginはtoken不要というV003制約へ整合。全12 PTはそれぞれの想定検査境界まで到達して成功。期待値をProductionから生成せずSQL制約/保護2件は変更しない。
