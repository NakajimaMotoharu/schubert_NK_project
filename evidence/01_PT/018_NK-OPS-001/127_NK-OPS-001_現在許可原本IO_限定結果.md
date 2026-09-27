# PG303 現在許可原本IO 限定結果

126/PT-OPS-PERMITFILE001～008 8/8＋関連28PT、failure/error/skip0。新subject全counter missed0/静的0。105collector負canary成功、Batch期待全数436へ明示登録したが全Batch436はまだ未実行。詳しいsource/suite/coverage/log/hashはprovisional/PG303/manifest.json。2026-09-27 22:05:13 JST、Java25.0.4/Maven3.9.12/JaCoCo0.8.15/SpotBugs4.10.4.0、dev-foundation/保存基点23520c264。

`JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -pl src/schubert-nk-batch test -Dtest=StartupPermitFilesTest,StartupPermitRecordsTest,InspectorEnvironmentPublisherTest,InspectorEnvironmentReaderTest jacoco:report spotbugs:check` exit0。最初のtestCompileはfixture closeの広いthrows ExceptionがWerrorに抵触してexit1、IOExceptionへ限定し警告を抑制せず修正。最初の8成功時に残った2境界は非空new partと読取buffer上限を満たす不正providerの拒否試験を追加して網羅、productionの除外なし。

実VM PT-OPS-NATIVE-020: marker確認したUbuntu26.04/Linux7.0/root/Java25.0.4でtools/quality/vm/NativeStartupPermitProbeを実行exit0。実tmpfs・root0700・0600/link1・CREATE_NEW permit・current ATOMIC_MOVE/readback・旧permit拒否・全ownercloseを確認した。テスト専用 `/run/schubert-nk/startup-pgpt-303` 新規namespaceだけ、現在recordは最後INVALID、Production真正原本・M/A/fullstep/issuer/business起動を代替しない。raw記録はGit外、公開boolean projectionとhashだけ保存。VMでprivate key/DBdumpを作成・格納していない。

本部品はまだProduction callerへ未接続のため、今回の検証粒度は変更Batch/直接関連suiteと実nativeIO限定。業務受入又はsecurity結線の横断変更時に451全回帰を行う。正式1964PT/53scope/run24・工程中心48.3%、R2/R3は不変更。次は473の実backup/cleanup/transfer/Broker/Expiry・fullroot/schema/Ops/current issuerをつなぐ。
