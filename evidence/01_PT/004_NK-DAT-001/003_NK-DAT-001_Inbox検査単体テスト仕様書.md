# NK-DAT-001 Inbox検査単体テスト仕様書

## 1. 対象・前提

Class/method: `dev.codex.schubert.nk.api.maintenance.InboxResponseInspector` constructor/isStructurallyValid。
関連: NK-DAT-001/NK-MSG-002、RD OPS-009/MQ-008、UI212/241/242/251、SS324 §12.1/331/341/352、QA-046/UIC-006/SSC-049、BUG-014/YKT-012、PG-D-119。
新規未実装部品のTDD。既存BUG-014の最終再試験とは別であり、構造検査の成功をDB参照・削除の成功へ計上しない。
秘密鍵はtest内でCSPRNG生成し、保存・出力しない。WireはSS322/323/234のoffsetから独立作成、暗号入力もproduction encryptを使わずJCE+Deflaterで生成する。Expectedはliteral true/falseと保存metadataであり、productionメソッドから生成しない。

## 2. Case一覧（実装前仕様）

| Test ID | method | 目的・入力/操作 | 独立期待値 |
|---|---|---|---|
| PT-DB-INBOX-001 | validSuccessAndErrorProfiles | GAMRSPの空/1/最大10record、0000/0200、各error codeを独立wire化・暗号化、COMPLETED/ERRORに対応させ検査 | 全てtrue、元暗号入力不変。ERRORは仕様どおりzero/space filler |
| PT-DB-INBOX-002 | headerAndMetadataMismatchesReject | identity/layout/version/owner/message・保存state/time、wire protocol/layout/kind/corr/time/len/context/reserved/codeを単独変更 | 各false、平文を返さず削除しない |
| PT-DB-INBOX-003 | payloadEncodingAndSemanticFaultsReject | DATA件数、record game/name/order/reserved、invalid UTF-8/非NFCを変更 | 各false。整合する日本語/NFCはtrue |
| PT-DB-INBOX-004 | cryptographicDamageAndMissingSnapshotReject | 暗号各位置改変、鍵version不明、異なるkey、snapshot欠落、閉codec | 各false、入力ciphertext不変 |
| PT-DB-INBOX-005 | exactLengthsAndTimestampPrecision | header未満/余剰/不足/1MB超、saved timeのmillis/μs境界 | 不整合false、同一millisのμs違いtrue、別millis false |
| PT-DB-INBOX-006 | nullContractsFailBeforeValidation | constructor/null identity/null completion | NPEを契約違反としてthrowしtrue/falseに変換しない |
| PT-DB-INBOX-007 | concurrentInspectionsDoNotShareState | 固定独立wireを100並行、異message混在、元ciphertextを保存比較 | 正常だけtrue、混線0、入力不変 |
| PT-DB-INBOX-008 | databaseReferenceIsNotCertifiedByStructure | 型として合法だが実在未検証のresult reference/未検査owner、responseがREQUESTの場合 | 参照そのものは本部品の判定対象外（正常構造true）、REQUESTはfalse。DB削除を行うI/Oなし |

## 3. 実行・品質・証跡

Java25/既存Maven・NullAway・SpotBugs・JaCoCo。探索は `./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -pl src/schubert-nk-api -am -Dtest=InboxResponseInspectorTest,FieldCodecTest,OwnedTransferDirectoryTest -Dsurefire.failIfNoSpecifiedTests=false test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check`。
正式判定はclean verify、全対象line/method/class/branch 100%、failed/error/skipped/flaky/not-runを除外。探索の部分coverageを正式合格に使わない。
実行日時/tool/branch/sourcecommit/command/exit、各case結果、coverage、sanitized証跡hashは004とevidence/manifestへ記録する。現時点は全8case未実施。
