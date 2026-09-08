# 閉SecurityContext・認証fixation探索

2026-09-08 JST/dev-web。SSC-044/PG-D-103/PT-WEB-068～075、実装前仕様616e314。FUN-001/AUT-001～004、UI226/232/234、SS314 §7.2.6/331/352。421既存Java25.0.4/Maven3.9.12/Spring Security7.1.1/Session4.1.1/PostgreSQL18.6、追加tool/dependencyなし。

| 探索 /tmp/PT-WEB-security-context- | 終了JST | 結果 | raw log SHA256（raw非格納） |
|---|---|---|---|
| explore-01 | 22:56:47 | Web13件中12PASS/1error、初期合成wire fixtureの識別子誤記。非合格 | b4501a8126ca11d1b45340b0c83512f2ecfc497265240b10e71b107578fce311 |
| explore-02 | 22:57:55 | Web13件PASS、新3class＋内部Deferred＋変更provider全coverage100%、静的解析0 | f75e039279ce4f26d4b235402cc78604e03c3b179ccaa39578a81927a7faebbd |

```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-web -am -Dtest=SessionSecurityContextTest,MqAuthenticationProviderTest,FieldCodecTest,OwnedTransferDirectoryTest -Dsurefire.failIfNoSpecifiedTests=false test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check
```

## 独立期待・範囲

初期PT075の新規手書きfixtureは先頭を誤ってSCHUBERTとした。UI232 §共通header第1fieldとSS322 §decodeの固定SCHBNK01を再確認しfixtureだけ訂正。既存productionは不正wireを固定UNAVAILABLEへ拒否しており仕様違反ではない。未完成TDD fixtureの準備誤りとして記録し、既存oracle/Current baseline/上位仕様不変更。初回errorは合格に算入しない。

通常HTTP/DB試験は実SessionRepositoryFilterと隔離PostgreSQL/Flyway/roleを使う。SessionRepositoryFilterの公開SESSION_REPOSITORY_ATTRの同一instanceを検査し、native fallbackを拒否する。未知principal型やget/set例外など実暗号adapterが生成できない不正container状態だけは、同公開markerとMockHttpSessionによる明示fault double。private class reflectionやproduction除外は使わない。

USER/ADMIN・username/context/loginAt・権限1個・credential/detailなしを明示比較。通常saveは現在requestの暗号session projectionと同値検査、追加commitなし。Login strategyは既存CSRF sessionから1回だけatomic fixation、独立sequence期待の新UUID/CSRF、Cookie属性、SavedRequest/未完了token保持、旧row消失/row1件をSQL確認。JSONの明示field値と汎用SecurityContext/credentials非混入も確認する。既存属性codecの完全golden vector試験は正式全回帰する。

全public null、未知marker/認証型/権限/属性、SQL open/update/commit/close/key故障を検査。DB commit後close故障は新rowがcommitされ得ることを明記し、rollback成功と偽らない。strategy失敗＋filter commit失敗時503/成功Cookieなし、plain sessionなし。後続HTTP失敗handler/孤立API context補償は別gate。

100 concurrent deferred参照は1回だけloadしprivate monitorで同期。実Holder filterは両role/匿名/再作成repository/expiry/暗号破損とcontroller例外を通しThreadLocal clearを確認。失効前request snapshotのsaveはキャッシュの同値検査であり最新API認可ではない。最終Spring session response commitが消失rowを拒否しINSERTしない。以後の業務ごとのAPI再認証は必須。

独立UI232/234 byte offsetのLogin0000/0200＋GAM0000/0102を実provider→strategy→context save→次HTTP復元へ接続。Password入力消去、probe回数、新CSRF維持、失効replay非grantを確認する。合成wireであり実API/JMS起動や実NK Characterizationを主張しない。

## 正式gate

正式PT-WEB-20260908-12、sourcec807a3838f983056015f1d92ab063731dcd89a37、22:59:37～23:04:06 JST、exit0。全700件（Protocol80/Storage34/API394/Web151/CHR41）、Web75件、新8件を含めfailed/error/skipped0。全5対象module line/method/class/branch100%、NullAway/Enforcer/format PASS、SpotBugs0。全7collector/manifest/hash更新、SSC-044当該範囲完了。次のRequestCache PT076～081は未実行で本gateに含めない。最終form/handler/Logout/起動/実NK CHR、IT/STは未完了。
