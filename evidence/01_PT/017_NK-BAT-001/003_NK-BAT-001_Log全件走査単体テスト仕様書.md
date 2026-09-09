# NK-BAT-001 Log全件走査 単体テスト仕様書

## 1. 対象・前提

PG-D-138、RD OPS-009/DAT-009、UI251、SS341 §3・7.2/331 §3.9/332 §11.4、SSC-051、BUG-104/YKT-092/012。
LogCleanupService・LogCleanupSummary・CleanupStoppedException。実PG18/Flyway、固定run/backup2step/公開log、独立long件数/時刻・公開JDBC故障注入を用いる。OS/実backup/main/全batchは未完了の別gate。

| Test ID | method | 事前条件・入力・操作・独立期待値 |
|---|---|---|
| PT-BAT-018 | emptyAndCompletedRuns | 空run→END/0、既完了は保存累積のみ・二重加算なし、autoCommit/接続生存 |
| PT-BAT-019 | heldPrefixAndLargeChunks | hold10000＋後続eligible1、各row一度だけ計上、累積10001/1/10000・WARNING、保全行不変 |
| PT-BAT-020 | resumedAttemptCounts | 事前確定2/0/2から開始し1/1/0だけattempt差分、run3/1/2・WARNING |
| PT-BAT-021 | sessionLockOwnership | 同一parent connection既取得lock再入、完了後親lock保持、未取得は自己分だけ解放、他connection競合は無変更 |
| PT-BAT-022 | backupAndRowLockStop | missing/FAILED backup・先頭loglockは未完了reason、後続削除/再試行なし |
| PT-BAT-023 | timeBoundaryAndClockWrap | 30分前/一致/超過・後退/自然wrap、chunk前後判定、壁時計でcutoff変更なし |
| PT-BAT-024 | interruptsRemainSet | 開始前/途中/終了直前の割込で未完了・flag不変、他の例外を成功へしない |
| PT-BAT-025 | rollbackAndUncertainCommit | SQL/commit前失敗はrollback、commit後の通信故障は未完了・同run再読で真の累積回復 |
| PT-BAT-026 | restorationAndUnlockFailures | autoCommit復帰/rollback/lock解放の各故障を成功にしない。rollback失敗後の暗黙commit禁止 |
| PT-BAT-027 | invalidInputsAndProjections | null・既存transaction接続拒否、lockのNULL/欠落/多重/false、破損累積、DB例外redaction |
| PT-BAT-028 | summaryInvariants | 初回/最終/run同一性、非負差分/保存完了、正常・全矛盾/null/long上限、secret非表示 |
| PT-BAT-029 | failuresLeaveNoFalseSuccess | 全SQL/resource failure後に成功summaryなし、失敗connectionはcallerがclose、予期外runtime伝播 |

## 2. 判定・証跡

BUG-112の方式確定: 最初のchunk結果と同transaction内の累積から開始件数を差引復元する。PT018～020の独立開始/終了/attempt期待値は不変。2chunk目以降は復元開始値と直前確定累積の一致をcommit前に確認し、PT027/029で不整合を注入する。非公開backup helperの直接実行やgrant追加は行わず、既存cleanupのBACKUP_GATE/LOCK_BUSYをそのまま使う。

実行command/OS/JDK/tool version/branch/source/日時/exit/line-method-class-branch100%/Test ID/BUG/関連file/hashを004・evidenceへ固定する。Sourceからexpectedを生成しない。固定10001行と差分は算術/SQL後条件を使い、同Production methodからexpectedを生成しない。
探索29件/新12件成功は004参照。正式全体gateまでは未合格。TDDの初回未実装失敗以外は915を修正前起票。Failed/flaky/skipped/not-runを合格へ含めない。
