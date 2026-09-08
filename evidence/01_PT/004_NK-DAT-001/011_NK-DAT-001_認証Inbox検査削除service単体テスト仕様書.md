# NK-DAT-001 認証Inbox検査削除service単体テスト仕様書

## 1. 対象・契約（実装前）

`AuthenticationInboxCleanup`のconstructor/inspectNext/内部JDBC境界、`InspectionRun`、`InspectionStep`、`InboxMaintenanceException`。RD OPS-009/DAT-009/MQ-008、UI212/241/251、SS324 §12.3/331 §3.5/332/341/343/352、QA-046/UIC-006/SSC-049、PG-D-122。ProductionはAPI module maintenance package、PTはAuthenticationInboxCleanupTest、結果は012。

SqlConnectionProviderは毎回freshな専用role connectionを返し、serviceが単独所有・closeする。run/cutoffは不変record、cursorはOptional UUID。runはJDBC/固定長日時で表現可能な0001～9999年・microsecond精度とし、null/範囲外/非microsecondを拒否する。keys/既知fingerprint version集合もprocess中不変。呼出し側nullはNPE契約違反、DB必須NULLはRequiredColumnのSQLDataException、未知/矛盾metadata・欠落snapshot・未知鍵は削除せず保護する。NPEをcatchして保護へ変換しない。

候補取得→列/整合検査→条件付き削除→commitを一つの非公開transactionで行う。SQL候補は最大1行、Message昇順。復号bufferを外へ返さない。内部結果はDELETED/PROTECTED/ENDと次cursorのみ（外部diagnosticは件数と固定理由へ集計）。記録のtoStringにはMessageやrunを出さない。ENDだけcursor空、他は必須。cursor/runを途中で差替えず、SAVEPOINT/外部callback/途中commit/外部connection公開を禁止する。

暗号/参照検査部品の統合falseは原因を断定せずPROTECTED（保護WARNING）とする。内部replayがまとめた復号不正・参照不一致・読取り失敗を正常成功と呼ばない。削除serviceから観測できるSQL・DB aborted state・commit/rollback/close故障は非秘密の失敗。検査後にtransaction healthを確認し、aborted transactionのCOMMITがROLLBACKへ変わるケースを合格にしない。原始SQL message/cause/suppressedを外へ出さない。SQL成否不明は正常削除完了とせず同run再走とする。

## 2. Test ID（未実施、期待値は独立）

| Test ID / method | 入力・操作・fixture | 期待値と根拠 |
|---|---|---|
| PT-DB-INBOX-033 / validAuthRowsDeleteAtomically | 独立JCE/SS322/323手組Login成功/0101/0106、Logout0000/0200/0102、7日経過、実V008/V009・専用role | 対象1削除、session/backup不変、DELETED、次回END。snapshot expectedは既存独立Fixtureで生成しproduction capture/encodeを呼ばない |
| PT-DB-INBOX-034 / invalidRowsAreProtectedWithoutMutation | 暗号破損/unknown key/参照missing・owner/hash不一致、canonical/version/期限/HMAC version不正、欠落snapshot | PROTECTED/保持・次cursor、PROCESSING/未期限/非認証は候補外。秘密値を結果へ含めない |
| PT-DB-INBOX-035 / nullUnknownAndFactoryContracts | constructor/run/cursor/要素null、空/未知config、mutable集合変更、DB NULL/不正enum/長さ/参照 | 境界の明示例外または保護。nullをdefault/0/emptyへ暗黙変換しない。既知versionの防御copy |
| PT-DB-INBOX-036 / ownsTransactionAndKeepsLocks | JDBC公開interfaceのfault/probe wrapper、候補後・delete前の別connection更新、commit/close観測 | 新規connection、autocommit=false、SAVEPOINT0、途中commit0、row/ref/backup更新55P03、成功commit1/close1。接続の外部公開なし |
| PT-DB-INBOX-037 / failuresRollbackAndRemainRedacted | open/autoCommit/prepare/execute/read/health/delete/commit/rollback/close故障、commit前後を別fixture | 未commit変更はrollback、必ずclose、固定非秘密例外/cause0/suppressed0。commit後故障では削除済の可能性を明示し再実行END、成功扱いしない |
| PT-DB-INBOX-038 / orderedCursorAndFixedRunReplay | 複数候補、最初が破損、次が正常、空/再実行/別run/backup不足 | UUID順に保護→削除→END、同run/cutoffでのみ進行、過去証明を新transactionへ使わない |
| PT-DB-INBOX-039 / concurrentAttemptsCannotDoubleDelete | 100並行・同一row、実専用connection・advisory競合を明示制御 | 削除1回だけ、他はENDまたは予定したlock競合例外。競合をflaky/skipとして除外しない。全futureを回収・connection終了 |
| PT-DB-INBOX-040 / keysAndResultsNeverEscape | current/previous/closed鍵、100回反復、入力/結果/toString、negative static gate | unknown/closedは保護、正常2世代成功、平文/鍵/session/cipher出力0、全class/method/line/branch100% |

## 3. 実行・証跡

421 toolchain、探索は新test＋既存Inbox検査3種/DB15を併走。正式root clean verify・NullAway・SpotBugs・JaCoCoのline/method/class/branch100%を必須とする。実環境/日時/source/branch/command/exit/Test ID/独立expected/actual/coverage/BUG/SSC/hashは012とsanitized manifestへ確定する。未実施/failed/flaky/skippedを合格にしない。PG/PTでありIT/STは未実施。
