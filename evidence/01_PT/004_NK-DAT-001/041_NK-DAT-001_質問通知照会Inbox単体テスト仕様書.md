# NK-DAT-001 質問・通知照会Inbox単体テスト仕様書

2026-09-09 V016回帰追補（SSC-049/PG-D-141、BUG-127/129・YKT-102）: 現在の独立catalog期待値はversion付きmigration001～016の16件、業務/technical計23table・PK23/FK23/UK constraint30/CHECK154/constraint trigger1。QWK partial unique indexはconstraint数へ混同せず045/PT192で別照合する。後述の初回V005～015等の値は当時の履歴であり、現在の回帰期待値には使わない。全31route・更新3成功のQUESTION/JOB、ERROR/NONE、168hと6種参照matrixは045/PT177～192および015/PT051～056へ追跡。各Programの実行結果・manifestにある正式sourceを正とし、未実行を合格へ含めない。

PG-D-139/SSC-049/QA-046/BUG-014/YKT-012。RD DAT-009/MQ-008/OPS-009/QST-005～010/NTF-001～012、UI212/232/234/236/241/251、SS324 §6/12.8・331 §3.10・332/341/352。
対象: NonAuthenticationInboxInspector.isConsistent、InboxCleanup.inspectNext/inspectStoredNext/runChunk、V015 maintenance_delete_inbox。試験class QuestionQueryInboxCleanupTest。新production classなし。

## 1. Fixture・独立oracle

isolated PostgreSQL18.6を既存Flywayで構築、実inspector roleと正常backup2step/run42/cutoff2026-09-17T00:00:00.123Z。response completed2026-09-09T00:00:00.123Z、owner7はsynthetic。current/previous鍵は毎回CSPRNG、snapshotはtest-only JCE/Deflaterによる独立暗号化。raw鍵/context/token/wire/dumpは証跡へ保存しない。
GoldenはUIのliteral領域offsetで作成: header256、NTS/QSS data48、NTS record624/QSS672/max50、NTD8896/QSD8352。page50、日時20260909090000123、public receipt26文字、synthetic本文。N/B正常zero、Xspace、errorはNzero/X・Bspace/record0。Production codec/registryをgolden作成/expected生成に使用しない。
期待値は下表のliteral boolean/outcome/SQL件数と時刻、DB/catalogの独立SELECT。現在の質問・通知rowが不存在でも過去照会snapshot/NONEは整合するが、誤AAD/参照/構造は保持。

## 2. Test ID

| Test ID | method | 入力・操作・期待結果 |
|---|---|---|
| PT-DB-INBOX-161 | queryProfilesAndFrozenSnapshots | 4layout×0000/0100/0101/0102/0103/0104/0105/0106/0107/0200/9000/9001。NTS/QSSは0000/9001、NTD/QSDは0000/0104だけtrue。明示transaction/owner7/NONE、業務rowなし・現在owner無効化/role変更後も同値、query実装済みとはしない |
| PT-DB-INBOX-162 | goldenBoundsAndSemanticDamage | NTS/QSS 0/1/50record、NTS全5state/3type、NTD5state/削除有無/回答空・4096byte、QSS/QSD回答3state。page51/record51、予約byte・NFC/UTF8/必須ID/日時/state/削除条件/回答日時矛盾はfalse。明示offsetで1変数ずつ変造 |
| PT-DB-INBOX-163 | canonicalIdentityReferencesAndNulls | null3引数は拒否、autoCommittrue/ownerなし・別owner/相関/version/key不明/暗号改変/欠落snapshot/全5型付きrefはfalse。QSB/NTC/QDL未検証は保持。SQL故障はfalse/owned入口は非秘密失敗 |
| PT-DB-INBOX-164 | validRowsDeleteAndRetainExactMetadata | 4route正常/許可error、NONE/owner/token/001/既知fingerprintをownedserviceへ投入→DELETED/row0/END。誤token/owner/ref/response/version/key/PROCESSINGは保持または候補外。DB本文/roleを変更しない |
| PT-DB-INBOX-165 | retentionBackupAndSqlAuthority | 24h前/一致/後1μsとstrict cutoffの差、backup成功2つ/不足/FAILED/lock、inspector以外のdelete42501・inspector業務本文SELECT42501。SQL全guard/旧24route回帰。期限更新だけで暗号合格を捏造しない |
| PT-DB-INBOX-166 | failuresRollbackAndResume | 実ownedserviceのdelete後/commit前/commit後不明/close故障を公開JDBCprobeで注入、失敗は固定例外・no cause。rollback保持/commit不明から同run再読・二重計上なし。行lock継続を確認 |
| PT-DB-INBOX-167 | concurrentAndDurableMixedRuns | 100並行snapshot検査は全期待値一致、fresh connectionの所有と閉鎖。混在4route正常/不整合/更新3未対応を永続runで走査、exact inspected/deleted/protectedとEND・同run再開で重複なし |
| PT-DB-INBOX-168 | appendOnlyInventoryAndClosedRoutes | literal15 migration/23table/CHECK154/全既存route回帰、V014 SHA固定、V015は4route以外意味不変・helper新grantなし・public/他role禁止・固定owner/search_path/UTC。SQL行列とJava4coverage100%を区別 |

## 3. 実行・判定・証跡

Java25.0.4+7/Maven3.9.12/JDBC42.7.13/Flyway13.4.0/JUnit5.13.4、固定repo/toolchainは421。探索はAPI -am verify、正式はclean source commitで work/pgpt_foundation_verify.sh の新run ID。全体build/NullAway/Spotless/Enforcer/SpotBugsとline/method/class/branch100%、全8 PT成功、failed/flaky/skipped/not-run0が必要。SQL WHERE/guardは165/168と既存PT049～056に明示対応、SQLのJaCoCo100%とは称さない。
正式対象commit/branch/日時/command/exit/結果・coverage/hashは042とevidence/question-query/manifest.json。018の全28scope同一run/source/branch/hash/参照確認必須。未実施は合格に含めない。BUG-014/YKT-012/SSC-049は更新3参照・main/OS/実backup等を残し本部品だけでは閉じない。
