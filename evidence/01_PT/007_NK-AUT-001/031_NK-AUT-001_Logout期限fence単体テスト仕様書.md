# 031 NK-AUT-001 Logout期限fence単体テスト仕様書

PG-D358/QA050/SSC171/BUG618/YKT437、S3/D05同Web起動経路の必要依存。RD AUT004/MON004、UI226232234、SS314 QA050補足/331/332/352。既存API Logout wire・Inbox ERROR snapshotを変更しない。PG447固定全6実行中は仕様だけを保存し、未実装・未実行を合格にしない。

| Test ID | 対象/事前条件・操作 | 独立期待値 |
|---|---|---|
| RERUN001-A | AuthSessionRevocationService/LogoutInboxService、実API roleの現在session、期限now直前/等しい/直後1µs、独立Clock・LOGREQ256byte | 直前/等しい=既定0102/280byte error、同TXでrevoked=true/reason EXPIRED/現在µs時刻・SESSION_REVOKED監査 reason EXPIRED/code0102・Inbox ERROR/NONE。直後=既定0000/LOGOUT。idle/expiry延長0 |
| RERUN001-B | 同MessageIDのERROR replayとfresh MessageIDの再Logout | 旧0102 ERRORはimmutable・再audit0。新MessageIDだけ検証済0200/元EXPIRED日時を返す。一般0102をWeb永久失効proofへ読替え0 |
| RERUN001-C | User/session lock前後でClockとTOUCH/expiry/fenceをlatch制御 | lock下fresh時刻/current expiryを再検証。古い認証nowが待機後でもrevokedを拒否・TOUCH0。先行TOUCHが延長した現在rowはLOGOUT0000。User→session順を維持/connection0/JMS待機中DB0 |
| RERUN001-D | 現rowをexpireし監査/update/row close/statement close fault、rollback/commit不明・unknown | SQL/fence/audit/Inboxを同TX rollbackして部分成功0、未知例外を成功化0。真正commit後の確認はfresh SQL、wireとfenceを別sourceで補完0 |
| RERUN001-E | 旧Instant入口、現在Clock入口のnull/空/未知context・inactive/既revoked/物理削除/時刻境界 | null契約をAPI境界で拒否、未知/物理削除は0102・偽fence/0200生成0、inactive有効期限は既定拒否、既失効は真正identity/日時検証。旧ADMIN revoke理由/SQLは不変更 |

FixtureはApiLogDatabaseFixture隔離PG18.6（運用DB/VM原本でない）、public literal時刻/UUID/contextだけを使う。expected wireはUI232234 header offsetと独立golden、hashはJCA独立SHA256、DB後条件はliteral SQL/µs UTC。Production methodからexpected生成を禁止する。

RERUN001-F（BUG622/YKT440追加）：`rerun001FatalCloseOfExpiredRowIsNotAnInfrastructureResponse`/`rerun001FatalMarkerMatrixKeepsIdentityAndSqlPrimaryCyclesAreBounded`は、期限fenceのDenied中ResultSet closeで重大Errorを注入する。AuthRevocation logoutCurrent/revokeAll、Verifier verify/inspectReadOnly、AuthSessionService issue、AdminCommandAuthenticator verifyIdentityの6実public入口＋同SQL-primaryのnested/cyclic suppressedを隔離PG/明示JDBC faultで制御する。期待=注入したErrorのidentityそのまま伝播・caller rollback後revoked/audit0、通常SQL/cyclic非fatalは固定Infrastructure message/cause null/suppressed0、循環で無限走査0。private呼出し/coverage目的の人工入口は使わず、既存SQL/close/fault/権限/Inbox試験も回帰する。

実method対応：A/B=`rerun001ExpiryBoundaryFencesAtomicallyAndPreservesErrorReplay`（3境界・audit JSON reason/code・immutable replay/fresh0200）、C=`rerun001CurrentClockIsReadAfterSessionLock`/`rerun001PriorTouchIsCurrentAndLateVerifierCannotUndoFence`（実row lock後Clock更新・先行TOUCHの現在expiry・User lock保持中の別transaction遅延認証拒否/TOUCH0）、D=`rerun001ExpiryFaultsRollbackFenceAuditAndInboxTogether`（7 update/audit/Inbox/statement-close faultとrollback SQL）。EはAuthSessionRevocationServiceTestの既存null/fault/旧Instant/ADMIN/unknown/既失効と新logoutCurrent全6null境界、LogoutInboxServiceTestのexisting owner/identity/fingerprint/snapshot-fault/100再送を併せる。副作用期待は独立literal SQL、wire280byteは固定offsetから作る。branch除外/無意味assert/実行中の別source借用なし。

実行はsource固定前の影響選択JUnit/strict compile/SpotBugs/JaCoCo全4counterと、変更契約群の同source fresh全6を組合せる。APIExpired単独をWeb retry/null期限/worker・native full readinessの受入としない。実行command/OS/JDK/tool/日時/source/終了code/XML/coverageとhashは032の実結果/manifestへ保存し、独立試験追加時にcase/対象methodを追記する。現時点は未実行・coverage未認定・関連障害対応中。
