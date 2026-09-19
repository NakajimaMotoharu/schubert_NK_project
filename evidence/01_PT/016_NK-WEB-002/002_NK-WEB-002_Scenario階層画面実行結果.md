# NK-WEB-002 Scenario階層画面実行結果

## 現在状態

PG194/SSC071の3階層画面に限定。選択16PTは成功、正式全reactorは未実行。Program全体・実NK Characterization gate・PGPT・IT/STの完了証明ではない。

## 選択試験

2026-09-20 05:16:58 JST終了、42.983秒、exit0。JDK25.0.4/Maven3.9.12、Ubuntu26.04.1、PostgreSQL18.6、dev-foundationのPG194作業tree。正式対象commitは後続manifestへ記録する。

```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-web -am spotless:apply test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check -Dtest=FieldCodecTest,ResourceScopeTest,ScenarioControllerTest,MenuMvcTest,ApiSessionInvalidTest
```

PT-SCR-001～016全成功、関連Menu6/APIinvalid8も成功。失敗/error/skipped0、NullAway/SpotBugs未解決0。controllerはclass1/method10/line72/branch25全到達、ScenarioMvcConfigurationは1/2/2/0、共有WebMvcConfigurationは1/9/33/0。branch0は条件分岐がないcomposition classで除外なし。正式clean verifyで既存全codeのcoverageと再確認する。

raw log `/tmp/pgpt-pg194-green4.log` SHA256 `6ee7b639626e67c7ba9d5dd65f6008b5c980f8292715e0a811de20234ce61c40`。raw credential/session/tokenをGitへコピーしない。独立goldenと期待HTTP/DOM値は001、実際値は全assert照合済み。公開合成trace012とsanitized結果16件・class coverage・source hashは029 collectorで正式runと結合する。

## 障害と横展開

- BUG213/YKT169: Class::castのnullable契約。ProductionのGame/Route/File全3変換を明示cast lambdaへ統一、NullAway成功。APIの既存test fixture1箇所はProduction境界対象外、既存回帰で確認。
- BUG214/YKT170: 共通JMS fixture上限128を既存契約12へ修正。16case実行・8worker/100要求の相関/応答/待機解放を確認。Production上限不変更。
- BUG215/YKT171: 新3templateのinline要素空白をCurrent同様に保持。Games card、Routes meta/nav、Files meta/navを独立literalで照合。menu/layoutは改行あり、block境界は非該当。expected/Current baseline不変更。
- BUG216/YKT172: 証跡scope41への増設に伴う固定count2箇所・failure loop1箇所を修正。019全59＋017全1canary成功。残る40 literalはGit SHA長でscope件数ではない。

上記は選択再試験成功、正式全reactorと同一commit証跡の確定後に台帳を完了へ更新する。実broker/bootstrap/全画面/Production request logging/実NK互換性gateは未完了。
