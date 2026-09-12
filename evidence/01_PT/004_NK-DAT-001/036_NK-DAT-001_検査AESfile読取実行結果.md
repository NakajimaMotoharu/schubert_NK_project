# NK-DAT-001 検査AESfile読取実行結果

2026-09-12 最新確定: dev-foundation/source 194667c104b091e2f303805b1a908602bbe52319、正式PT-WEB-20260912-03（21:44:36～21:52:02 JST）、全1133件（Protocol80/Storage58/API634/Web241/Batch79/CHR41）PASS、failed/error/skipped0。実装済み6 Java moduleのline/method/class/branch100%、Production5 moduleのNullAway/Enforcer/Spotless/SpotBugs未解決0。固定/runの限定静的レビュー1件は維持しcoverage除外なし、CHR runnerのSpotBugsは未設定。12collector/35scopeの同run/source/branch/hashと17負canary成功。DB26部品240＋batch3部品37＋OPS9部品66＝38部分成果343 PT（全1133の内数）、今回private0600/非上書き公開の低位能力8件を追加しBUG150/YKT116再試験完了。PG154/run環境publisher12件は仕様のみで未合格。親制御/backup artifact/設定publish/SSC055原本・全cleanup caller・通常Question writer/replay・Logout RERUN001・QA045は残る。固定加重約4割（35～50%、456）を維持、残件は460。実NK CHR/IT/ST完了とはしない。利用枠残94%でPG/PT継続中、元dev-web3file保全。以下は履歴。

探索2は2026-09-09 12:57:01 JST、32.456秒、exit0。dev-foundation/80b5da36後の未commit実装。新12＋旧AES16＋Storage24＋Protocol5=57件PASS、failed/error/skipped0、NullAway/Enforcer/Spotless PASS、SpotBugs0。関連6classのline94/method20/class6/branch50/instruction540全missed0。正式25は本sliceを含まず、全体回帰・証跡確定までは未完了。035/PT129～140、PG-D-134、SSC-049。

探索1はJUnit assertTrueの型推論がBooleanSupplier overloadへ衝突しtestCompile失敗、新12件未実行。BUG-098を修正前80b5da36で起票し、generic戻り値をprimitive booleanへ明示代入して同一assertを実行。新assertを弱めず、全同形検索で他該当0。

Command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-api -am -Dtest=FieldCodecTest,OwnedTransferDirectoryTest,LinuxInodeSecurityTest,InspectorAesCredentialTest,InspectorCredentialAccessTest,InspectorCredentialLoaderTest test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check`。作業log /tmp/pgpt-inspector-credential-loader-explore-2.log。正式manifestに環境/全tool/branch/source/日時/exit/実際値とhashを固定する。

必須/current欠落・previous open前不存在・途中missingを区別。実symlinkはnative/content open前に拒否。実ファイルの部分read/EOF、1byte過長、0/負/進捗偽装、属性/ACL/RO変化、channel/entry close、root再検証、rename/置換で逸脱せず保護。成功/不正parse/IO故障のbuffer全0、100独立loadの元key一致を確認。正常権限属性は明示された合成portであり、実system manager配布の合格ではない。実nativeとpolicyは031/033の個別試験に追跡。rootはcaller所有のまま。秘密値・file内容をsanitized証跡へ出さない。
