# 画面限定SavedRequest・暗号RequestCache探索

2026-09-08 JST/dev-web。PG-D-104/PT-WEB-076～081、実装前仕様8152762。FUN-001/AUT-001～004、UI221/226、SS313 §4/9・314 §3/7.2/352。421既存Java25.0.4/Maven3.9.12/Spring Security7.1.1/Session4.1.1/PostgreSQL18.6、追加tool/dependencyなし。公開RequestCache/SavedRequest/DefaultSavedRequest SPIは421記録のMaven Central release source jarで照合。

| 探索 /tmp/PT-WEB-request-cache- | 終了JST | 結果 | raw log SHA256（raw非格納） |
|---|---|---|---|
| explore-01 | 23:10:47 | NullAway nullable URI path1件、PT前compile失敗。BUG063、非合格 | 53a6cafffff91ea63bb7c12a11e2f807e8e80fc4e7171dc37a79b77de0b647e4 |
| explore-02 | 23:12:41 | Web18件PASS/新class全100%、SpotBugs1件（欠落parameter nullのSPI）、BUG064、非合格 | 0f891afbb91ed53030f3f16b80a51ecb05060f158a75749dd86934300d0dc95d |
| explore-03 | 23:15:11 | Web18件PASS、新2class＋SavedGet全coverage100%、静的解析0。BUG065 negative追加 | 8ab40011f3820986c7b3ae41b655bcfd0b4af870ea04c935ad00eb51ede4be6a |

```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-web -am -Dtest=SessionSavedRequestTest,SessionSecurityContextTest,SavedRequestTargetTest,FieldCodecTest,OwnedTransferDirectoryTest -Dsurefire.failIfNoSpecifiedTests=false test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check
```

01はSavedRequestTargetTestを除いたcommand。正式はroot clean verifyで実施し探索累積coverageを代用しない。

## 独立期待と実接続

UI221/SS313全保護HTML screen familyを手書きURL集合で指定し、game/IDの業務有効性・role/owner認可とは分離。Login/error/static/media/未知route、更新POST/HEAD等、AJAXを保存しない。UTF8長2047/2048/2049、日本語、空query、query内の?やsemicolon、encoded文字を正常値のまま対照する。正規化して別URLへ変更しない。Generic SavedRequestTargetのURL安全検査にscreen/secret policyを追加する外側factoryである。

実PG/Flyway/roleと実SessionRepositoryFilterでsave/get/match/remove/fixationを実行。保存属性はStringだけ。Host/header/Cookie/body/locale/parameterはSavedRequestへ複製しない。SavedRequestの不在parameterはSpringのnullable SPIに従い空map.get(name)で返す（DefaultSavedRequestと同じ関係）。空arrayへの期待変更や静的解析抑止を行わない。全getter/null/immutable projectionを確認し、exact current GETだけ同requestを返して保存を消費。既存GETをPOSTで上書きせず、追加body/headerを復元しない。

100実sessionを異なるqueryで並行保存/読取し、公開monitorを保持しても進み、保存内容が混ざらない。失効前snapshotのsave/remove/responseは削除rowを新規INSERTしない。Login fixation後のSavedRequest消費はprincipal/CSRF/未完了tokenを変更しない。SQL open/update/commit/close/key失敗は503/成功Cookieなし。Commit後closeでDBが確定する可能性をrollback済みと誤認しない。

## 障害と全対象確認

| ID/対象 | 修正または非該当根拠 | 再発防止 |
|---|---|---|
| BUG063/YKT057 SavedScreenTarget | 検証済URLを二度URIへparseしてnullable pathをmatcherへ渡す処理を廃止。最初の?で非null String path/queryを分離 | PT076/077、queryなし/空/複数?・外部/opaque/fragment/Unicode、NullAway0 |
| YKT057 SavedRequestTarget raw path | 既存getRawPath直後の明示null拒否で保護、修正不要 | PT005～008全再試験、null/opaque URI/外部/2048byte |
| YKT057 normalized path | 非null String.equalsの引数だけでnullable結果をdereferenceしない、修正不要 | PT006 dot segment/normalize負例 |
| YKT057 raw fragment | null比較だけ、dereferenceなし。再parse raw queryは新classから除去 | PT006/077 fragment拒否とquery値保持 |
| BUG064 SavedGet array getter | 空parameter mapを単一projectionとしてget(name)へ委譲、欠落=nullの公開SPIを維持 | PT078全getter・不在/null、SpotBugs0。全production getParameterValues検索で他array返却実装なし、FormCsrfは別のServlet読取契約のため916追加不要 |
| BUG065 screen target URL carrier | reviewでpath parameter/標準session query名の欠落を発見し修正前8c196ee起票。semicolon/%3b path、JSESSIONID/SCHUBERT_NK_SESSION queryをfactoryで拒否 | PT077の保存前拒否、080の不正stored read拒否、正常query値semicolon保持。両cache入口は同factoryへ集約し、他のHTTP SavedRequest writerは未実装。単一factoryの不足であり別共通原因の916追加なし |

BUG063/YKT057は8826908、064/065は8c196eeで修正前起票。Unknown stored型/get/set/remove例外は公開Mock Servletのfault doubleで注入し、本物の暗号adapterが未知型を作るとの主張はしない。上位仕様/Current baseline/正常oracleは不変更。

## 正式gate

次のroot clean verify/全7collectorで確定予定。最終EntryPoint/Login success/failure handler/全chain/実API/JMS/画面/実NK CHRは未実装・非合格、IT/ST完了を主張しない。
