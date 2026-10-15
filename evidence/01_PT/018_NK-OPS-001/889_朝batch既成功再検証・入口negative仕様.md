# 朝batch既成功再検証・入口negative仕様（実行前）

PG3366、Production a9/PG2802、WBS-P017-01/11。関連OPS009/BAK001/UI251・253/SS331§8・332・341・343/SSC077078089094。既全3350/3352/3354=3704/542/1643・同28nativeは比較基点で、新Testへ成功を先取りしない。Main/DDL/配備/VM操作は変更0。

| Test ID | 入力・操作/独立期待値 | 後条件・非主張 |
|---|---|---|
| PT-BAT-EXP3366-001 / ExpiryAuditRepositoryTest#exp3366001PriorSuccessRevalidatesEveryReadbackWithoutMutation | 実隔離PostgreSQLの手書きSUCCESS row(id42/target2/success2/failure0/byte200/cutoff20260905T150000.000500Z)。公開JDBC proxyで一箇所だけduplicate selection、missing readback、null selected rows、WARNING status、future ended、missing ended、error code、error summaryへ変える。各一注入を独立counterで確認しBatchRepositoryException/causeなし/固定redaction、trusted元run resolverは固定RUN。元SQL row/audit全値をliteral比較し、各故障後の通常SUCCESS完全値と同handleを再読 | proxyの全取得済statement/ResultSetを一close・live0、借用connectionはopen/autoCommitfalseのまま、元rowにwriteなし。NULL endは共有read validationで拒否されても正しいが、外側重複条件の枝を被覆したとは主張しない。実master/原本DBを使わず、実SQL schemaに反する値をDBへ書込まない |
| PT-OPS-MCTRL019 / MorningControlScopeTest#mctrl019NativeEntryNullContractsNeverReachTrustedWork | native入口のlegacy/owned/epoch、明示resumeのrun/work、verified/completedのbudget/work/optional-runを各nullで独立投入。内部非null契約違反としてNPEを伝播し、callback呼出しcounter0。valid budgetは公開Linux単調clockから生成する読取だけで、Root capture前のguardを検査 | Unit/DB/M-A/原本操作を一切発行しない。正常Rootの代替や全wrapper受入ではなく、nullを新規run/未指定resume/clockリセットへ読み替えない契約のnegative PT。ProductionがNPEをcatchして正常化することは禁止 |

期待値はProduction methodから生成せず、DDL fixtureのSQL literalと明示結果を使用。成功actualをexpectedへコピーせず、不変確認の前にも元row literal一致をassertする。秘密key/token/session/masterを保存しない。関連は全六moduleで各実suiteを含むselected groupを一回、厳密NoTests/FES-flaky-notrun0・静的0・全1643Main/resource/debug同byteを検証し、次必要統合へまとめる。現時点未実行/未受入、正式1964/53・15/190・工数null/QA051final保留は不変。群予算はevent0888の.3/.9/2.2pp、実費/N/T未取得null。
