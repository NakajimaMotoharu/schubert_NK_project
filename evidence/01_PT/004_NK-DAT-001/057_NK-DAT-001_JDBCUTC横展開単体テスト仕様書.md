# JDBC UTC境界 横展開単体テスト仕様書

実行更新: 正式PT-WEB-20260913-03/source6d4dc743で全1223件/6 module4coverage100%/静的解析PASS・36scope/22canary成功。DB249/250と全対象の既存Program回帰は058/quality-context/manifestへ対応し、BUG167～170/YKT128～131/SSC056を完了。以下の先行仕様の「未実装・未検証」は作成時点の記録であり、今回の対象を前回1205件へ加算しない。

BUG169/YKT130追加（先行22051162、修正前）: 旧Timestamp.fromの範囲外IllegalArgumentExceptionに代わりOffsetDateTimeはDateTimeExceptionを投げる。固定infrastructureを約束するAdminCommandAuthenticator/UserCommandService/UserQueryRepository/LoginAttemptRepository/AuthSessionRevocationService.logout/JdbcWebSessionStoreでは同じ固定外側例外とrollback/所有を維持する。既存ADM012/020に加え、既存ADM005・LoginAttemptのJDBC負PT・Logoutのfault PT・WEB028にMIN/MAXまたはMINの直接境界を追加する。対象クラスのcatchへ特定DateTimeExceptionを加え、未知runtime/NPEを包括正常化しない。単純Instant値を受ける低位adapterで元からunchecked invalid-clockを伝播する契約と、BatchRun/InspectionRun・wireの年範囲invariantは変更しない。

PG160/SSC056/BUG167/YKT128、先行8002b28b/3cf06b00・SS332/352 a1ebcabd。DAT-003～011/AUT-001～004/ASY-001～009/MON/OPS-009、UI225/226/231/241/242/251。修正開始前仕様。既存Program境界・Test IDを維持して以下を追加する。

| Test ID | class/method | 独立期待値・fixture |
|---|---|---|
| PT-DB-INBOX-249 | RunReferenceBoundaryTest.jdbcUtcVectors | PostgreSQL typed timestamptzの手書UTC literal/epochとJDBC4.2 bind/projection。0001、1582-10-04/05/14/15、1900、1970、現代µs/JST日付境界、9999。UTC/JST/NewYork sessionで同Instant、全6桁保持、SQL NULLはnull。Timestamp反例は修正前auditに保存し正常値へ混ぜない |
| PT-DB-INBOX-250 | RunReferenceBoundaryTest.productionUtcBoundaryInventory | 修正対象23 Production classを独立一覧、legacy java.sql.Timestamp/from/getTimestamp/setTimestamp・java.sql.Date/getDate/setDateを全src/mainで禁止。UTC OffsetDateTime bind/typed projectionを各対象で確認し、既存Program別業務PTと組み合わせる。単なるファイル検索だけでYKT完了にしない |

23対象のProgram別回帰と追加歴史時刻観点:

| Program | Production class（各既存method全対象） | 対応PT/確認 |
|---|---|---|
| NK-MSG-002 | JdbcOutboxRepository、JdbcInboxCoordinator | OutboxDispatcher/JdbcInboxCoordinator/BoundInboxExecutionの既存PT、lease/retry/完成/再送時刻・NULL/fault保持、DB249/250 |
| NK-AUT-001 | LoginAttemptRepository、AuthSessionService、AuthenticationContextVerifier、LoginReplayService、LogoutReplayService、AuthSessionRevocationService、LoginAuditWriter、SessionAuditWriter | 同名/関連Login・Logout・Audit PTの全SQL下限/TTL/参照/暗号snapshot・null/projection fault、DB249/250 |
| NK-ADM-001 | UserCommandService、UserQueryRepository、UserAuditWriter、UserRequestAuditWriter、UserQueryAuditWriter、LogQueryRepository、LogQueryAuditWriter | 既存User/Log/管理監査PT、時刻検索bound/表示µs→ms・locked_until任意nullと物理型fault、DB249/250 |
| NK-DAT-001/NK-MSG-002 | InboxCleanup、WebLogIngestService | 全Inbox候補/永続進捗/検査・WebLog ingest PT、原本cutoff/completed/期限とDB249/250 |
| NK-WEB-001 | JdbcWebSessionStore、WebLogOutboxRepository | 既存technical session/outbox PT、生成/更新/期限/leaseのtyped read（前者projectionは元から4.2）とDB249/250 |
| NK-BAT-001 | CleanupRepository、RunReferenceRepository | BAT001～017/018～029/082～089、原本cutoffと独立SQLの年0001進捗一致、全16 JDBC位置のmethod統合後も全occurrence故障 |

機械変更はparameter順・SQL・型付きnull・invariant・例外・connection所有を変えない。setTimestamp/getTimestamp用probeはsetObject/getObjectへ更新し、既存同名故障点と合流する場合は全呼出し位置を残して確認する。fixtureだけの型変更でexpectedをProductionから算出しない。NULLや旧合法年を除外してcoverageを作らない。

Source/試験/SQL literalの変更をcommitに固定し、全reactorでline/method/class/branch100%、NullAway/SpotBugs/format、全Programの独立PT/同run証跡/負canaryを再実行する。対象一覧の修正/元から非該当/追加vector・再試験証跡とhashをBUG167 auditへ記録し、既存Current baseline不変を確認する。現在は未実装・未検証の横展開仕様であり、前回1205 PTの認定へ遡及追加しない。
