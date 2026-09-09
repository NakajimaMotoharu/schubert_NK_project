# NK-DAT-001 検査AESfile読取実行結果

最新正式判定: PT-WEB-20260909-30/source15cb454a、2026-09-09 14:30:10～14:36:41 JST、dev-foundation、exit0、全967件・6 Java module全4種coverage100%・静的解析0。当scope全Test ID成功、evidence/credential-loader/manifest.json SHA-256 `1dac7a564c78c3d3796ee6724218891a2be1f333463d38bfdf797b5d0048b8b7`。全27scope同時点性/hash/参照と017の1件・019の4件負canary成功。DB19部品160件＋batch repository17件確定。BUG-109～111/YKT-096/097再試験完了。BUG-104/SSC-051のSQL永続走査・親repository読取は成功、全件走査service/OS/main/backup gate/7参照/全Program完了は残件。本slice合格と工程全体の合格は区別する。以下は旧正式・探索履歴。

探索2は2026-09-09 12:57:01 JST、32.456秒、exit0。dev-foundation/80b5da36後の未commit実装。新12＋旧AES16＋Storage24＋Protocol5=57件PASS、failed/error/skipped0、NullAway/Enforcer/Spotless PASS、SpotBugs0。関連6classのline94/method20/class6/branch50/instruction540全missed0。正式25は本sliceを含まず、全体回帰・証跡確定までは未完了。035/PT129～140、PG-D-134、SSC-049。

探索1はJUnit assertTrueの型推論がBooleanSupplier overloadへ衝突しtestCompile失敗、新12件未実行。BUG-098を修正前80b5da36で起票し、generic戻り値をprimitive booleanへ明示代入して同一assertを実行。新assertを弱めず、全同形検索で他該当0。

Command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-api -am -Dtest=FieldCodecTest,OwnedTransferDirectoryTest,LinuxInodeSecurityTest,InspectorAesCredentialTest,InspectorCredentialAccessTest,InspectorCredentialLoaderTest test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check`。作業log /tmp/pgpt-inspector-credential-loader-explore-2.log。正式manifestに環境/全tool/branch/source/日時/exit/実際値とhashを固定する。

必須/current欠落・previous open前不存在・途中missingを区別。実symlinkはnative/content open前に拒否。実ファイルの部分read/EOF、1byte過長、0/負/進捗偽装、属性/ACL/RO変化、channel/entry close、root再検証、rename/置換で逸脱せず保護。成功/不正parse/IO故障のbuffer全0、100独立loadの元key一致を確認。正常権限属性は明示された合成portであり、実system manager配布の合格ではない。実nativeとpolicyは031/033の個別試験に追跡。rootはcaller所有のまま。秘密値・file内容をsanitized証跡へ出さない。
