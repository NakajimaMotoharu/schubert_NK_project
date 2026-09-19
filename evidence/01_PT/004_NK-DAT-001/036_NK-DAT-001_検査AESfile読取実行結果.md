# NK-DAT-001 検査AESfile読取実行結果

2026-09-20 最新確定: dev-foundation/source50ebfa27026736b702d723f7e11a482495b6cc0d、正式PT-WEB-20260920-11（04:47:50～04:59:36 JST、Maven11:44/exit0）、全1528件（Protocol80/Storage82/API689/Web269/Batch367/CHR41）PASS、failed/error/skipped0。6Java全line/method/class/branch100%、Production5 NullAway/Enforcer/Spotless/SpotBugs未解決0、固定path3method限定review/coverage除外なし、CHR SpotBugs未設定。17collector/40scope整合・58負canary成功。DB29/266＋Batch25/281＋OPS17/142＋QST2/16＋ASY1/5＋Web3/28＝77部分成果738PT（全1528の内数）、今回再開比+113PT/+12部分成果。PG190空回答providerを限定認定、workerは未実装。PG193階層表示12PTを限定認定、BUG212/YKT168完了。PG194/SSC071の実画面は仕様のみ。BUG195/206/YKT154/162/SSC063、実archive/親/質問受付全体/Web/Logout/QA045/実NKgateは未完了。固定加重約4割（35～50%）、残量52%で継続、元dev-web3file保全、PGPT/IT/ST未完了。以下は履歴。

探索2は2026-09-09 12:57:01 JST、32.456秒、exit0。dev-foundation/80b5da36後の未commit実装。新12＋旧AES16＋Storage24＋Protocol5=57件PASS、failed/error/skipped0、NullAway/Enforcer/Spotless PASS、SpotBugs0。関連6classのline94/method20/class6/branch50/instruction540全missed0。正式25は本sliceを含まず、全体回帰・証跡確定までは未完了。035/PT129～140、PG-D-134、SSC-049。

探索1はJUnit assertTrueの型推論がBooleanSupplier overloadへ衝突しtestCompile失敗、新12件未実行。BUG-098を修正前80b5da36で起票し、generic戻り値をprimitive booleanへ明示代入して同一assertを実行。新assertを弱めず、全同形検索で他該当0。

Command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-api -am -Dtest=FieldCodecTest,OwnedTransferDirectoryTest,LinuxInodeSecurityTest,InspectorAesCredentialTest,InspectorCredentialAccessTest,InspectorCredentialLoaderTest test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check`。作業log /tmp/pgpt-inspector-credential-loader-explore-2.log。正式manifestに環境/全tool/branch/source/日時/exit/実際値とhashを固定する。

必須/current欠落・previous open前不存在・途中missingを区別。実symlinkはnative/content open前に拒否。実ファイルの部分read/EOF、1byte過長、0/負/進捗偽装、属性/ACL/RO変化、channel/entry close、root再検証、rename/置換で逸脱せず保護。成功/不正parse/IO故障のbuffer全0、100独立loadの元key一致を確認。正常権限属性は明示された合成portであり、実system manager配布の合格ではない。実nativeとpolicyは031/033の個別試験に追跡。rootはcaller所有のまま。秘密値・file内容をsanitized証跡へ出さない。
