# NK-DAT-001 Inbox投影Resource境界 実行結果

2026-09-28 JST。branch `dev-foundation`、修正source/test/spec commit `2cbf70ae2636fec283ff9fa0c25df405a1c259fe`。対象PT-DB-INBOX-267 A～H・268、BUG-319/YKT-162。70番仕様に示した独立SQL/transaction oracleを維持した。

修正前RED: 公開JDBC proxyの`result_ref_type` getterへ未知IAEを注入したPT-DB-INBOX-267の初回選択1件はexit1/failure1。「固定InboxMaintenanceExceptionが必要だが例外なし」で、PROTECTEDへ降格したことを確認。fixture installのJaCoCo check不達、無試験reactorのMaven失敗、修正中の`Instant` import不足はこのREDにも合格にも算入しない。

修正後: 8 getterすべてを値変換catchの外へ移し、保存値enum/modelだけの不正は従来PROTECTED、provider未知IAEは固定cause-free失敗へ分類。PT-DB-INBOX-267 A～Hはcommit0/rollback1/close1/Inbox1、PT-DB-INBOX-268は永続progress0・同run正常再開後1/1/0・END・Inbox0。選択2 suite/18 testはF/E/S0、SpotBugs0。API moduleのclean runは744 test/123 suite F/E/S0/SpotBugs0。JaCoCoの`InboxCleanup`外側classはinstruction986/986、branch80/80、line168/168、method15/15、class1/1でmissed0。

461/451に従う横断確認triggerは、owned Inbox削除・永続cursorの状態変化と共有Bootstrap試験fixture変更。保存済sourceからProduction6の`clean test spotbugs:check jacoco:report`を実行しexit0、2,432 test/356 suite、F/E/S0、6 module SpotBugs0。module別test数はProtocol80、Storage149、Bootstrap175、API744、Web555、Batch729。全体coverage missed(branch/line/method/class)はProtocol0/0/0/0、Storage0/0/0/0、Bootstrap37/11/4/0、API1/19/3/0、Web1/19/3/0、Batch15/235/92/12。よって全Production4指標100% gateは不合格であり、正式`PT-WEB-20260925-24`/source`858713c0bf310ae8bf62078b0a1cedbce4e968db`の認定値1964PT/53scopeを更新しない。JS適用coverage、全scope/hash collector、CHR、実NK、R2/R3は本限定実行に含まれない。

再現環境: Linux host、JDK25.0.4、Maven wrapper3.9.12、固定offline repository、Node24.19.0、JaCoCo0.8.15、SpotBugs4.10.4.0、隔離PostgreSQL18。実行command、開始/終了、exit、入力/期待/実際、sanitized結果、local raw XML・coverageのSHA-256、源file/spec SHA-256は[evidence manifest](evidence/provisional/PG354-inbox-provider/manifest.json)を正とする。manifest SHA-256 `67dc84b648b0d70fc64b8d1098c349d1bbabd2b471fd937f32be5fa8b2c7e60e`。raw JDBC/credential/session/cipher/token/stack traceはGitへ保存せず、保存した`results.xml`はTest IDと合格状態だけ。

BUG-319の直接修正・再試験は完了。ただしYKT-162の他JDBC/JMS/IO所有者全件とYKT-154は未完了。外部Morning/Backup Unit、Web/API Production process、実NK CHR-A01/L01、PGPT全体完了は未達。
