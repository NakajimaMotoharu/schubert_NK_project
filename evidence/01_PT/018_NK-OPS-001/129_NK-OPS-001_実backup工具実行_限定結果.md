# PG304 実backup工具実行 限定結果

128/PT-OPS-ARCHPROC001～008 8/8＋関連56PT、failure/error/skip0、新subject全counter missed0/静的0。105負canary成功、Batch予定全数444は全件未実行。source/suite/coverage/log/hashはprovisional/PG304/manifest.json。Java25.0.4/Maven3.9.12/JaCoCo0.8.15/SpotBugs4.10.4.0、dev-foundation/保存基点22613db35、最終関連64PT 2026-09-27 22:27:41 JST。

`JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -pl src/schubert-nk-batch test -Dtest=BackupArchiveProcessTest,BackupBundlePublisherTest,BackupBundleCompletionTest,BackupManifestPublisherTest,BackupArtifactVerifierTest jacoco:report spotbugs:check` exit0。最初のNullAway nullable filename dereference/testのlambda capture compile失敗は修正して保持、静的/警告の抑制なし。

BUG270/YKT204: 初期8PT成功後、dumpとrestore-listの期限再設定を修正前起票。独立clock 0/0/29分/30分の再現試験は8中1failed（Expected IOException but nothing thrown）として保全。公開dump開始を一度取得し、開始前/全waitへ共通budgetを使用、修正後はlist起動0・tar/age後段も同期限で拒否/owner消費を確認。既存BundlePublisher/Verifierのshared started実装・関連PTも再確認、未実装親全backupの総deadlineは後続接続条件で成功に算入しない。

VM native021は実root/保持親FD/固定tar→ageを公開fixtureだけで実行exit0。暗号文をGit外開発機へ取り出し、既存private recovery keyで復号、tar内公開fileが独立53bytefixtureとcmp完全一致（終了0）。ciphertext/復号tarのhashだけmanifestへ記録、private key/recipient値/plain archive/filename一覧/rawstderrはGitに置かない。実DBdump/systemd backup credential配布・manifest/DBstep成功/7世代/fullmorning/business main/CHRは未達。実dumpへ向けてVMbackup roleはlogin可/superuser不可/createrole不可/password未設定、backup-pgpass未配置をread-onlyで確認、既存credentialの上書きなし。

今回classは既存Production callerへ未接続のためBatch/直接依存限定。認可やshared credential結線の横断変更/機能受入時は451全回帰。正式run24/1964PT/53scope/48.3%、R2/R3は不変更。
