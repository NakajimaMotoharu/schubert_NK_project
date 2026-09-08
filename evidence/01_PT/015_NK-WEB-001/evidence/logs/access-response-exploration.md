# 未認証・role拒否接続探索（PT-WEB-125～130）

dev-web、基準8a5cb6a＋新handler/factory/6PT。先行仕様e52ae82/PG-D-112。Java25.0.4/Maven3.9.12/Spring Security7.1.1/Session4.1.1/PostgreSQL18.6、隔離DBと合成request/actor/wireだけを使用。raw Cookie/CSRF/context/password/exception/JVM logをGitへ保存しない。

```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-web -am '-Dtest=SessionAccessFailureTest,WebSecurityAuditTest,WebAuthorizationFilterTest,FieldCodecTest,OwnedTransferDirectoryTest' -Dsurefire.failIfNoSpecifiedTests=false test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check
```

探索01は2026-09-09 01:35:48 JST終了exit0、Web16件（新6＋audit6＋認可4）、Protocol5/Storage16成功、failed/error/skipped0、NullAway/Enforcer/format PASS、SpotBugs0。新handler line37/method4/class1/branch10、新factory line5/method2/class1/branch0を100%。変更audit line58/method7/class1/branch40、認可factory line20/method3/class1/branch0も全coverage100%。branch0はcompositionのみであり条件を除外したものではない。原本/tmp/PT-WEB-access-20260909-explore-01.log SHA256 697891c359af3a84892ebc1d8cd76e8bb5ed54c0f8f1f9e2e565660aa01697dc。

独立期待はUI221の通常GET302/login・POST/AJAX/media403、閉SavedRequest、SS351固定JSON/actor省略/ROLE。入力/例外diagnostic未参照をcanaryで、DB/attribute/logger/response faultを公開seamで検査。実PG Session/Holder/CSRF/Login/ExceptionTranslation/Authorizationの連結で、匿名GETの暗号保存→匿名POST非再送→Login後復帰→USER管理403/ADMIN通過を確認。100並行のID/actor/status/Location分離とThreadLocal clearを確認する。

未認証イベントは既存AUTHORIZATION_DENIEDの理由UNAUTHENTICATED追加。既存6event期待は維持し、PT095へ独立7行目、PT096へactor混入拒否を追加。Sourceへの行為・counter変更に合わせて既存期待を緩和していない。新障害なし。BUG-072/YKT-064の全非回帰は正式runで確認予定。

正式PT-WEB-20260909-08（sourcef8d84a47d79be73436587a4583aa5637933d8ecb、01:37:22～01:41:54 JST）は全755件/全5module coverage4指標100%/静的解析0・7collector成功。Web130method完全一致、BUG-072/YKT-064の全非回帰も成功。環境/command/原本log hash/全counterはmanifest.json。

共通error HTML、runtime logger WARN固定、単一FilterChainProxy/本番bootstrap、API0102 local失効/owner検証・実NK Characterization/IT/STは未完了。
