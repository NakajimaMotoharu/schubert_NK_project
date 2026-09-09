# NK-DAT-001 全Inbox検査削除service単体テスト仕様書

## 1. 対象・oracle（実装前）

InboxCleanup（旧AuthenticationInboxCleanup）のconstructor/inspectNext/canonicalと参照検査分岐/内部JDBC、InspectionRun/Step/Exception。NK-DAT-001/MQ-008/OPS-009/DAT-009、UI212/234～237/241/251、SS324 §12.5/331 §3.6/352、QA-046/UIC-006/SSC-049/PG-D-125/BUG-014/YKT-012。既存011/PT033～040の認証回帰を全て維持し、非認証変造rowの候補外ENDだけを承認された全候補走査のPROTECTEDへ更新する。

新期待値は独立UI TSV手組wire、独立JCE snapshot、literal SQL後条件・固定clockとUUID順から作る。Production codec/capture/判定をexpected生成に用いない。元のrequest password/HMACを再計算できたとは扱わない。秘密/平文/wireを証跡へ出さない。結果018。

## 2. Test ID（未実施）

| ID / method | fixture・入力・操作 | 期待値・独立根拠 |
|---|---|---|
| PT-DB-INBOX-057 / validQueriesAndMutationsDeleteAtomically | 22routeの0000/許可ERROR、ULK0200、User参照、SCN I/F、24h/168h後、専用role | 対象1だけDELETED、他table不変、次END。正常例は独立wire構造も先行assert |
| PT-DB-INBOX-058 / userAndScenarioReferencesStayProtected | User/id/version/missing、Scenario/id/game/descriptor/missing、暗号・未知鍵 | 不整合PROTECTED/1保持、更新・file IOなし。後続正当versionは許容 |
| PT-DB-INBOX-059 / canonicalMetadataAndTokensAreRequired | 未知/別route/version/owner/token/HMAC version、期限不足、NULL constructor | protectedまたは明示例外、暗黙変換しない、未期限/PROCESSINGは対象外 |
| PT-DB-INBOX-060 / mixedCursorsNeverSkipUnverifiedRows | 未知→破損→User→queryのUUID順、同run/cutoff再走 | PROTECTEDもcursor返却、削除対象だけ消失、全候補を通過、再走は保護rowだけ残る |
| PT-DB-INBOX-061 / transactionFaultsRollbackAndResume | query/User/SCNの参照/DELETE/health/commit/close故障、aborted state | 失敗は正常扱いせず固定例外、未commit削除rollback、commit後不明は同run再走END |
| PT-DB-INBOX-062 / concurrentMixedRequestsStayIsolated | 100並行、同Message・複数候補、task-local JDBC probe | 削除重複なし、55P03だけ予定競合として許容、他SQLSTATE/未観測は失敗、全future回収 |
| PT-DB-INBOX-063 / leastPrivilegeAndKeyLifetimes | 専用roleでUser/SCN参照、delete直前別connection NOWAIT、current/previous/closed key | 参照/Inbox/backup lock継続、commit1/close1/SAVEPOINT0、鍵closeは保護、禁止権限42501 |
| PT-DB-INBOX-064 / outcomesAndSideEffectsRemainBounded | 反復/no rows、N9/retention境界、unknown7応答、redacted結果 | 警告を成功に数えず、出力は3状態/cursorだけ、業務行/秘密非変更・漏洩なし、4種coverage100% |

## 3. 実行と合否

JDK25/Maven/PG18等421、source/branch/command/日時/exit/expected/actual/coverage/BUG/SSC/hashは018とsanitized manifestへ確定する。V010新8 SQL、旧認証8、非認証参照8、既存DB15等を併走し正式root clean verify・全PT・NullAway/SpotBugs・line/method/class/branch100%でのみslice合格。未実施/failed/flaky/skippedは未完了。oneshot/全run/Question通知検査/V006置換/実NK CHR/IT/STは未完了。
