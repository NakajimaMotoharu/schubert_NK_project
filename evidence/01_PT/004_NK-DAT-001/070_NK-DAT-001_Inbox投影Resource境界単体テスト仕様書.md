# NK-DAT-001 Inbox投影Resource境界 単体テスト仕様書

Program: NK-DAT-001。対象は`InboxCleanup.read/owned/inspectStoredNext`、試験`AuthenticationInboxCleanupTest`と`InboxInspectionProgressTest`、公開JDBC proxy fixture`MaintenanceJdbcProbe`。RD MQ-008/OPS-009、UI241/251、SS324§12.3/12.5/12.6・331§3.5、442の固定Infrastructure分類、BUG-319/YKT-162を関連付ける。保存値の不正はPROTECTEDだがprovider実行障害を不正保存値へ降格してはいけない。RD/UI/SS正本の期待値は変更しない。

| Test ID | 目的・前提・入力・操作 | 独立oracle・期待値 |
|---|---|---|
| PT-DB-INBOX-267 A～H | 隔離実PostgreSQLへ正当Login `0101`を1件投入。公開`ResultSet` proxyの`result_ref_id/type/uuid`、`processing_state`、`response_key_version`、`completed_at`、`inspection_xact/hash`各getterへ未知IAEを1箇所ずつ注入。`inspectNext`を実行。 | SS324のowned transaction規則から固定cause-free `InboxMaintenanceException`。commit0/rollback1/Connection close1、Inbox行1のまま。8箇所ともPROTECTED/DELETED/ENDを返さない。SS322/323の独立fixtureで正当rowを作り、production `read`から期待値を算出しない。 |
| PT-DB-INBOX-268 | 正当Game `0000`を1件投入。`result_ref_type` getterに未知IAEを注入し`inspectStoredNext`を実行後、同runを正常providerで`runChunk`再開。 | 最初は固定cause-free失敗、commit0/rollback1/close1、Inbox1・進捗行0。再開時だけ手書SQL後条件`inspected/deleted/protected=1/1/0`・END、Inbox0。provider異常をPROTECTEDと永続化しない。 |

既存PT-DB-INBOX-033～040/081～088の不正保存値、null、欠落、既知SQL、provider close、同run再送、100並行競合、暗号独立vectorを回帰する。fixtureの`runtimeColumn`は試験専用でProductionを変更しない。合成private markerやrow/cipher/credentialは証跡へ出さない。修正前REDは267単独で1 failure/exit1を確認し、合格には算入しない。

実行環境はLinux/JDK25.0.4/Maven wrapper3.9.12、隔離PG18、branch`dev-foundation`。選択commandは`./mvnw -o -pl src/schubert-nk-api -Dtest=AuthenticationInboxCleanupTest,InboxInspectionProgressTest test spotbugs:check jacoco:report`（`JAVA_HOME`、固定local Maven repository、`nk.pt.repository`指定）。全module/全Programの正式認定は451に従い別判定する。対象source commit、実行日時/exit/coverage、BUG再試験、redacted manifestとhashは071結果および`evidence/provisional/PG354-inbox-provider/manifest.json`に記録する。選択成功だけでProduction全4指標100%、実NK、PGPT完了を主張しない。
