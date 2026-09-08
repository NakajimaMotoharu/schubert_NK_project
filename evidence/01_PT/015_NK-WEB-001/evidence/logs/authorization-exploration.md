# URL認可policy探索（PT-WEB-121～124）

dev-web、基準43bab25＋新factory/4PT、先行仕様7c68e04/PG-D-111。Java25.0.4/Maven3.9.12/Spring Security7.1.1、実StrictHttpFirewall/AuthorizationFilterと合成Mock request/閉principal。secret-bearing object/生JVM出力は保存しない。

```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-web -am '-Dtest=WebAuthorizationFilterTest,FieldCodecTest,OwnedTransferDirectoryTest' -Dsurefire.failIfNoSpecifiedTests=false test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check
```

探索01終了2026-09-09 01:23:00 JST、exit0。新Web4件/Protocol5/Storage16成功、factoryはline16/method2/class1すべて100%、branchは条件分岐0（設定compositionのみ、分母からの除外なし）。独立URL×role/method/dispatcherの条件はfixtureで網羅し、依存library自体のcodeを自作coverageへ算入しない。NullAway/Enforcer/format PASS、SpotBugs0。原本/tmp/PT-WEB-authorization-20260909-explore-01.log SHA256 3a84b09a17b186b89c9d7baf3d9f175163862619a6f0cf89f46a3863b2728c51。

6明示public URLだけ匿名で通過、ADMIN9URL/業務22URL/未知static/suffix等とUSER/ADMIN/anonymousの独立matrixを検査。9種不正pathとTRACEはfirewall拒否、encoded通常文字のadmin/logsはROLE_ADMINのまま。REQUEST/ERROR/ASYNC/FORWARD/INCLUDE全5dispatcher、100並行・下流0/1回・ThreadLocal clearを確認。Header/form/queryでroleを与えても権限値に採用しない。

探索中の新障害なし。正式runの全module gate/collector後に確定する。Login案内/403 view/監査handler/最終chain/runtime・IT/ST・実NK Characterizationは未実施。
