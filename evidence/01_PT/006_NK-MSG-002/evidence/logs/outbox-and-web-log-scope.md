# PT-IDEM-20260906-01 Outbox/Web log 中間実施範囲

実行commit、時刻、tool、command、終了code、coverageは同directoryのrun-summary JSONを正とする。
実装修正 `342c41b`、Web codec/SSC-007 `3fcf754`。BUG-009～012直接再試験PASS。

| Test ID | 実行class/method | 独立期待値・観測結果 |
|---|---|---|
| 009 | OutboxDispatcherTest.claimsOnlyDueExpiredRowsWithTenSecondLeaseLimitAndNoDispatcherOverlap | due<=now、lease<nowまたはNULLのみ。102件fixture中最大100、10秒lease、二つの未commit transactionのclaim ID集合は重複0 |
| 010（部分） | markSentAndFailureRequireLeaseAndUseExactBoundedRetryState、dispatcherPersistsBothDestinationsAndArtemisSuppressesSendMarkCrashDuplicate | 自ownerだけSENT/ERROR更新、新ownerを上書き0。send commit後mark前crashをlease移譲で模擬し、同一IDの再送を実brokerが抑止、queueは1件、回復SENT。consumer業務UK後条件は未実施 |
| 010（部分） | resultTimesFollowTheObservedJmsFailureAndCommitAfterElapsedSendTime | claim00:00:00、失敗00:00:03、retry00:00:04.100。04.099ではclaim0、04.100ではclaim1、07.100のJMS確認でsent_at=07.100 |
| 010（部分） | retryJitterReachesTheDatabaseAtEveryBaseAndContinuesAtTheAttemptCap、OutboxPolicyTest | 900/1000/1100、4500/5000/5500、27000/30000/33000、54000/60000/66000、270000/300000/330000ms。attempt99→100、100→100でも再送ERROR、保存nextは全固定表一致 |
| 010（部分） | initialReceiptSendKeepsItsExactDueTimeWithoutSamplingRetryJitter | enqueueのdue/sent時刻を制御Clock値に一致、jitter supplier呼出0 |
| 011 | persistedQwkPayloadIsFullyDecodedBeforeOpeningJms、publicBoundariesRejectNullModesBoundsErrorsAndEveryWireIdentityMutation | QWK data offset0/26/38/50、length26/12/12/14の独立golden。14種×2 destinationのpayload改変およびheader/row改変をJMS open0で拒否 |
| 012（部分） | WebLogPayloadCodecTest全8 method | 2336byte全wireをcurrent AESでNKENC1化し独立envelope/AADへ一致。previous読出、unknown拒否、8 AAD要素/length/row/tag改変拒否、長さ/null/close/100並行nonceを確認。dispatcher/ingest/HTTP非置換は未実施 |

## 横展開（YKT-009/010）

| 対象 | 判定・根拠 | 確認/再発防止 |
|---|---|---|
| API OutboxJmsSender | 保存bodyは外部DB境界なのでheaderに加え全field/semantic再decodeへ修正 | 上記011、独立goldenと単項目改変 |
| Web ArtemisRequestSender/JmsRequestReplyClient | In-memoryの既encode requestのtransport責務。SS312では業務form→typed payload→encoderの検証が上流であり、保存body再読ではない | 既存ArtemisRequestSenderTest/JmsRequestReplyClientTestを全体再実行。業務service追加時のtyped encode結線は後続Programのtrace対象であり未実施 |
| API JmsMessageFactory/ReplySender | In-memoryの既encode replyのtransport責務（SS312/321）。保存body再読ではない | 既存OutboundJmsAdapterTestを再実行。snapshot replayのdecode/rehydrateとtyped encodeはSS324に従い後続service接続で確認 |
| API FatalDlqMessageWriter/DlqSender、Web ArtemisReplyDlqSender | SS321 §11の不正原文/type保持が責務。再decodeして拒否するとDLQ隔離不能になるため非該当 | 既存fatal body/type不変、property allowlist、commit/rollback testを再実行 |
| WebLogPayloadCodec | 保存暗号bodyを認証後に全WLGEVT01 field/semantic decode、row identity照合済み | WebLogPayloadCodecTestのencrypt前/decrypt後同一改変matrix |
| API Outbox clock/retry | 結果時採時・注入jitterへ修正済み | 上記010の3秒進行/全段階境界/初回send0採取 |
| Web log dispatcher | 未実装。codecだけで配送の時間契約までPASSにしない | YKT-009/010はこの対象のfull decode接続/Clock/retry/再試験完了まで対応中 |

共通原因の検索だけで横展開完了とはしていない。後続3種AES用途とWeb dispatcher/ingestが残る。
