# NK-WEB-002 Scenario階層画面実行結果

## 現在状態

正式認定: PT-WEB-20260920-12/source0d0abbb80e91d016f961042e9b9e09cb07b5f7a9、dev-foundation、2026-09-20 05:24:36～05:36:26 JST、Maven11:48/exit0。全1544PT（Protocol80/Storage82/API689/Web285/Batch367/CHR41）、failed/error/skipped0。6Java全line/method/class/branch100%、Production5のNullAway/Enforcer/Spotless/SpotBugs未解決0。固定path3methodの既存限定静的reviewは維持、coverage除外追加なし、CHR SpotBugs未設定。18collector/41必須scope・60負canary成功。

新PT-SCR-001～016とcontroller1class10method72line25branch、config2class11method35line/branch0を再確認した。BUG213～216/YKT169～172は全対象の修正/非該当根拠・再試験を確認し完了、SSC071は3階層画面の内部具体化範囲だけ完了。raw log SHA256 `15da7275771ea9caffb9e20ae050feb5195f1d1e94d9a32f0fc1ac0614e1a8be`。正式command/環境/source・11file hash/16ID対応・coverage/公開012 traceはevidence/manifest.json参照。

PG194/SSC071の3階層画面に限定。Program全体・実NK Characterization gate・PGPT・IT/STの完了証明ではない。以下は選択試験履歴。

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

上記の選択結果に加え、冒頭の正式全reactor・同一commit証跡を確定した。実broker/bootstrap/全画面/Production request logging/実NK互換性gateは未完了。


P01504再送記録の原16＋graph4＋新fatal5全25仕様は[4121](../015_NK-WEB-001/4121_P01504再送記録原十六・新五全二五件単体仕様.md)。元19328成功は原source維持、未実行をPASSへ加算しない、費用主担当P01504一度だけ。

[4121 再送記録通常25](../015_NK-WEB-001/4121_P01504再送記録原十六・新五全二五件単体仕様.md): PG27508-REVOCATION25固定全25成功、原赤3失敗別記/target2四100・全scopepartial・原WBS未受入。

[4123 失効暗号通常16](../015_NK-WEB-001/4123_P01505失効暗号原七・新五全十六件単体仕様.md): PG27548-REVOCATION-CRYPTO16固定全16成功、原赤3失敗別記/target2四100・全scopepartial・原WBS未受入。


WBS-P016-01公開source契約/独立期待値/TestIDは[4126_P01601Login画面原二artifact契約対応.md](4126_P01601Login画面原二artifact契約対応.md)。metadataのみ、新PT/coverage/正式受入0。


WBS-P016-02公開source契約/独立期待値/TestIDは[4127_P01602Menu画面原四artifact契約対応.md](4127_P01602Menu画面原四artifact契約対応.md)。metadataのみ、新PT/coverage/正式受入0。

[4128 共有TraceMenu通常24](../006_NK-MSG-002/4128_P00603共有Trace原十五・新五全二四件単体仕様.md): PG27610-TRACE-MENU24固定全24成功、原赤3失敗別記/実target全四100・全scopepartial・原WBS未受入。

[4129 CaddyContext通常24](../015_NK-WEB-001/4129_P01502CaddyContext原十五・新五全二四件単体仕様.md): PG27630-CADDY-CONTEXT24固定全24成功、原赤5失敗別記/実target全四100・全scopepartial・原WBS未受入。


WBS-P016-03公開source契約/独立期待値/TestIDは[4130_P01603SCR003検索入力結果原四artifact契約対応.md](4130_P01603SCR003検索入力結果原四artifact契約対応.md)。metadataのみ、新PT/coverage/正式受入0。


WBS-P016-04公開source契約/独立期待値/TestIDは[4131_P01604SCR004Game一覧原二artifact契約対応.md](4131_P01604SCR004Game一覧原二artifact契約対応.md)。metadataのみ、新PT/coverage/正式受入0。


WBS-P016-05公開source契約/独立期待値/TestIDは[4132_P01605SCR005Route一覧原二artifact契約対応.md](4132_P01605SCR005Route一覧原二artifact契約対応.md)。metadataのみ、新PT/coverage/正式受入0。


WBS-P016-06公開source契約/独立期待値/TestIDは[4133_P01606SCR006File一覧原二artifact契約対応.md](4133_P01606SCR006File一覧原二artifact契約対応.md)。metadataのみ、新PT/coverage/正式受入0。


WBS-P016-07公開source契約/独立期待値/TestIDは[4134_P01607SCR007本文通信組立原九artifact契約対応.md](4134_P01607SCR007本文通信組立原九artifact契約対応.md)。metadataのみ、新PT/coverage/正式受入0。


P01608/09の個別契約と/2不足は[4137_P0160809Animationメニュー一覧個別契約対応.md](4137_P0160809Animationメニュー一覧個別契約対応.md)。metadata準備のみ、原16/DOM43は元source参照・新PT0。
