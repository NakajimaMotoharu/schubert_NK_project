# URL認可policy探索（PT-WEB-121～124）

dev-web、基準43bab25＋新factory/4PT、先行仕様7c68e04/PG-D-111。Java25.0.4/Maven3.9.12/Spring Security7.1.1、実StrictHttpFirewall/AuthorizationFilterと合成Mock request/閉principal。secret-bearing object/生JVM出力は保存しない。

```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-web -am '-Dtest=WebAuthorizationFilterTest,FieldCodecTest,OwnedTransferDirectoryTest' -Dsurefire.failIfNoSpecifiedTests=false test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check
```

探索01終了2026-09-09 01:23:00 JST、exit0。新Web4件/Protocol5/Storage16成功、factoryはline16/method2/class1すべて100%、branchは条件分岐0（設定compositionのみ、分母からの除外なし）。独立URL×role/method/dispatcherの条件はfixtureで網羅し、依存library自体のcodeを自作coverageへ算入しない。NullAway/Enforcer/format PASS、SpotBugs0。原本/tmp/PT-WEB-authorization-20260909-explore-01.log SHA256 3a84b09a17b186b89c9d7baf3d9f175163862619a6f0cf89f46a3863b2728c51。

6明示public URLだけ匿名で通過、ADMIN9URL/業務22URL/未知static/suffix等とUSER/ADMIN/anonymousの独立matrixを検査。9種不正pathとTRACEはfirewall拒否、encoded通常文字のadmin/logsはROLE_ADMINのまま。REQUEST/ERROR/ASYNC/FORWARD/INCLUDE全5dispatcher、100並行・下流0/1回・ThreadLocal clearを確認。Header/form/queryでroleを与えても権限値に採用しない。

後続のSS352 §3.1再照合で、Login匿名公開はGET/POSTなのに本探索のfactory/oracleが全method許可だったことを発見し、BUG-072/YKT-064を修正前起票した。探索01とrun07の機械的成功は、この設計不整合の合格根拠にしない。run07はsourcebad8beb959ae355144e406beee679ac44f5a04b4、01:25:17～01:29:49 JST、全749件/全coverage100%/静的解析0/exit0だが設計照合NGとして未確定。原本/tmp/PT-WEB-20260909-07.log SHA256 ebd5853ad5b38665cb8a7d6db08fd10b982f3b7307c17e5a988d2d2bd05d9c98。015 collectorによる合格確定を行わない。

修正後の探索02は同command、01:31:51 JST終了exit0、新Web4/Protocol5/Storage16成功、NullAway/format/Enforcer PASS/SpotBugs0。原本/tmp/PT-WEB-authorization-20260909-explore-02.log SHA256 885a993ad9f38726fdcc1878f536bc87c4caf8e48a3c311e892b5e14417e9ee4。Login GET/POST、static/error GET/HEAD、内部ERROR /errorだけ全methodを許可する厳密path×method表へ修正。外部POST/errorと管理URLのERROR再入は匿名拒否、正規エラー描画だけ許可する。全既存Login processing/converterはPOST限定で非該当（PT082～090/118の正式再回帰待ち）。上位正本は変更しない。

Login案内/403 view/監査handler/最終chain/runtime・IT/ST・実NK Characterizationは未実施。
