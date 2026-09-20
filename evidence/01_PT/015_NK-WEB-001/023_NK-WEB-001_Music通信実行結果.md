# Music一覧通信実行結果

PG210/PT-WEB254～261、仕様022。選択成功、正式全体回帰待ちで新8件は未加算。

初回 /tmp/pgpt-pg210-selected.log は2026-09-20 09:21:49 JST/25.191秒/exit1、Web testCompile失敗・新8PT未実行。SHA256=df81d47c9a2766cb1f1e82ce95829c1b15b90ecc6a53a32997aa3dee9aeab6b0。BUG223/YKT179をeec777beへ修正前起票。JMS wildcardの同名IllegalStateException衝突をJMSException/JMSRuntimeException明示importへ修正、Production/oracle不変更。全src Java検索でwildcard対象は新1fileだけ、既存Animation/Scenario/JMSは明示import。再発防止は全module compileとtransport/未知例外同一性/diagnosticの回帰。

再試験 /tmp/pgpt-pg210-green.log は09:23:30 JST/32.771秒/exit0、SHA256=15cdcd5d4b164350a994534f36059bf1ca9e47e0be3ebe33cb2d0e92dd99509e。Web32（新Music8/Animation8/Scenario8/JMS8）と依存PT成功、failed/error/skipped0。新1class2method5line全missed0、条件分岐0で除外なし。共通engine既存branchも回帰し、NullAway/Spotless/SpotBugs未解決0。MCT/MCS/MTR独立byte/最大20・100・200/all error/壊れた相関・context・profile/role・pair・順序/null/64並行/所有buffer消去は全assert成功。

```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -Dnk.pt.node=/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node --no-transfer-progress -pl src/schubert-nk-web -am spotless:apply test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check -Dtest=FieldCodecTest,ResourceScopeTest,MusicWireClientTest,AnimationWireClientTest,ScenarioWireClientTest,JmsRequestReplyClientTest
```

sourceeec777be＋PG210作業tree/dev-foundation、Ubuntu26.04.1/Linux7.0.0-31/amd64/JDK25.0.4/Maven3.9.12。015collectorに8ID/2source/022023、019独立inventory負canary追加で74成功、017の1を含む正式75予定。BUG223/YKT179は正式回帰まで未完了。HTTP/配信/実broker/実NKgate・PGPT/IT/ST未完了。正式対象commit/環境/command/日時/exit/coverage/path/hashはmanifestへ保存予定。
