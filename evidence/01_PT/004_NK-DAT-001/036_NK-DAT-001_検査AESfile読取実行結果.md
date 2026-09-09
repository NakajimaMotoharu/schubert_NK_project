# NK-DAT-001 検査AESfile読取実行結果

最新正式再試験: PT-WEB-20260909-39/source2236df45、2026-09-09 19:02:57～19:09:57 JST、dev-foundation、exit0。全体1059件（Protocol80/Storage42/API626/Web241/Batch29/CHR41）、6 Java moduleのline/method/class/branch100%、Production5 moduleの静的解析PASS。対象Test ID・個別結果・coverageはevidence/credential-loader/manifest.json、SHA-256 `a455783540f56735404e1f2229ea6656e014eaa4b62eff6405e372378af090b2`。全34scope/11collectorの同run/source/branch/hash/参照、017の1件・019の10件負canary成功。Current baseline不変、秘密pattern scan0hit。更新3参照は045/046、DB credential/接続は047/048、外側resource寿命は049/050で合格、通常writer/replay・main/oneshot・親OS/実backup/実NK CHRは未完了。以下は個別試験・過去の探索履歴（旧件数/hashを現在値に用いない）。

探索2は2026-09-09 12:57:01 JST、32.456秒、exit0。dev-foundation/80b5da36後の未commit実装。新12＋旧AES16＋Storage24＋Protocol5=57件PASS、failed/error/skipped0、NullAway/Enforcer/Spotless PASS、SpotBugs0。関連6classのline94/method20/class6/branch50/instruction540全missed0。正式25は本sliceを含まず、全体回帰・証跡確定までは未完了。035/PT129～140、PG-D-134、SSC-049。

探索1はJUnit assertTrueの型推論がBooleanSupplier overloadへ衝突しtestCompile失敗、新12件未実行。BUG-098を修正前80b5da36で起票し、generic戻り値をprimitive booleanへ明示代入して同一assertを実行。新assertを弱めず、全同形検索で他該当0。

Command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-api -am -Dtest=FieldCodecTest,OwnedTransferDirectoryTest,LinuxInodeSecurityTest,InspectorAesCredentialTest,InspectorCredentialAccessTest,InspectorCredentialLoaderTest test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check`。作業log /tmp/pgpt-inspector-credential-loader-explore-2.log。正式manifestに環境/全tool/branch/source/日時/exit/実際値とhashを固定する。

必須/current欠落・previous open前不存在・途中missingを区別。実symlinkはnative/content open前に拒否。実ファイルの部分read/EOF、1byte過長、0/負/進捗偽装、属性/ACL/RO変化、channel/entry close、root再検証、rename/置換で逸脱せず保護。成功/不正parse/IO故障のbuffer全0、100独立loadの元key一致を確認。正常権限属性は明示された合成portであり、実system manager配布の合格ではない。実nativeとpolicyは031/033の個別試験に追跡。rootはcaller所有のまま。秘密値・file内容をsanitized証跡へ出さない。
