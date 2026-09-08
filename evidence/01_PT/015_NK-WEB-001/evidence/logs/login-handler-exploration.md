# Login結果handler探索（PT-WEB-113～120）

dev-web、基準1e5ae28＋新2handler/8PT、先行仕様45e30b6/SSC-046/PG-D-110。Java25.0.4/Maven3.9.12/Spring Security7.1.1/Spring Session4.1.1/PostgreSQL18.6。合成username/password/context/wireだけを使用し、原本JVM出力/電文/credential/Session/Cookie/CSRF値をGitへ保存しない。

Command（repository root）:

```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-web -am '-Dtest=SessionLoginHandlerTest,FieldCodecTest,OwnedTransferDirectoryTest' -Dsurefire.failIfNoSpecifiedTests=false test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check
```

探索01は2026-09-09 01:14:00 JST終了exit0。新Web8件/Protocol5/Storage16成功、fail/error/skipped0。新MqLoginSuccessHandlerはline21/method2/class1/branch2、新MqLoginFailureHandlerはline33/method2/class1/branch8を全coverage100%。NullAway/format/Enforcer PASS、SpotBugs0。原本/tmp/PT-WEB-login-handler-20260909-explore-01.log SHA256 898342b6ce6cb871ef8373e23996839320b3c7308726c385139c20ac338beddf。

独立期待はCurrent handlerの302/Location、UI226/SS314/351のRetry-After0..900、サービス障害503、手書wire response、固定JSON key/actor/IP/ID、DB row数/旧ID不在/新principal。成功は保存済GETまたはrootへ戻り、任意target/Refererを参照しない。失敗例外のmessage/cause参照をAssertionErrorにするcanary、session未生成/DB行0、100並行で結果・監査の混入なしを確認。Actual Session/Holder/CSRF/form filter→provider→custom fixation→本handlerで0000/0200/0101/0106/9000/JMS故障を再現した。API test transportは既存SessionFormLoginTest.Apiの独立offset fixtureをpackage内で共有し、production encoderをexpectedに使わない。

PT120はfixation確定後のLocation設定故障で成功UIを返さず、旧rowなし・新row1・新principal・再Loginなしを確認。HTTP障害を既に確定したDB transactionのrollbackと捏造しない。再読取/handler再試行でもsession ID/CSRFを再発行しない。

新障害は検出されていない。全module正式coverage/証跡収集後にSSC-046を完了する。Login viewの残時間引渡し、全URL chain/logger/共通error view、実runtime/IT/ST/実NK Characterizationは未実施。
