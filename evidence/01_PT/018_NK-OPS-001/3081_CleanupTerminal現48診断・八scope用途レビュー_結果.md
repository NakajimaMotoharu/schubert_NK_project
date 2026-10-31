# CleanupTerminal 現48診断・八scope用途レビュー 結果

保存追補：修正commit fc2189382d4626464f895af48e8b8a7db734baea/push75391真正0（6751be）。全旧二失敗と新版/全proofを16064 SHA72a1503c1dd579844a559aba0cc82f0de28b3aa168293b84ae2a41ed2da9f0cfへ保存。BUG2155/56・YKT1902/03は当工具の有限対象だけを台帳で完了、全F03/実資源/元PT/正式は未受入のまま。

2026-10-31 / PG-D984 / 3080 / event3403。Main626行/SS332/331を静的に読むだけで、Product/DB/VM/Root等0。

| proof（evidence/provisional/配下） | manifest SHA256 | actual |
|---|---|---:|
| PG16058-cleanup-terminal-current-static-review-v1 | ca58d40993d3e8c9cf3cd008c64de040be242f306adf474e7274da5eb4946864 | 0 |
| PG16060-cleanup-terminal-review-failure-record-v1 | 2a0d587a701081929a4b47c4d9ffbb185a36d728322e22386407318c36795372 | 1（OUT前） |
| PG16061-cleanup-terminal-review-failure-record-v2 | ed01ed1056164c3d2cf76768aa04ab178e9a3ed37bdede28c7842ee3d22716e0 | 1（OUT前） |
| PG16062-cleanup-terminal-static-review-post-v3 | e90975ebb96f20ed8edf0c29d970a8f5a699271a462030f6d8fcac22e21c47c9 | 0 |

entryは4dcaad/60b5ae/5d1743/6595da、すべてlint0/body開始。最初の独立checkerはreplace引数だけsecondaryへ変えてthrow failureを残したため0match（BUG2155/YKT1902）。次は旧row/query二名称仮定でprogressSealのcheckedを拒否（BUG2156/YKT1903）。両工具と失敗を凍結し、その場再実行0。最初のfailure recordのregex match0は、凍結patternと現sourceからの静的再構成であり、元toolが数値をprintしたという意味ではない。全48/833の独立認定は16062真正0まで保留し、二失敗を合格へ加算しない。

新版はcleanup引数とthrowの同一捕捉symbolをbackreferenceで束縛し、aliasは別の宣言regexからsymbol/同resourceを取得してPMD tokenへ結合した。PARSER001～011（正3/負8）、ALIAS001～008（正3/負5）、META001～028（negativeLabelsの記録順）を管理Test IDとする。元raw/tool期待を呼んでexpectedを生成せず、方法境界/行/引数/tokenから全八を再構成した。旧16004/16006と二失敗工具のhashも固定。管理検査47をProduct PTへ加算0。

| method | resource | alias/body/finally/cleanup/end line | body catch | 形状 |
|---|---|---|---|---|
| read | rows | 190/206/209/213/217 | SQL/RTE/Error | 通常 |
| read | statement | 183/218/221/225/229 | SQL/RTE/Error | 通常 |
| references | rows | 289/311/314/318/322 | SQL/IO/RTE/Error | IO伝播 |
| references | statement | 281/323/326/330/334 | SQL/IO/RTE/Error | IO伝播・Entry prior;非実行local |
| progressSeal | rows | 376/381/384/388/391 | SQL/RTE/Error | brace無しnullguard |
| progressSeal | statement | 367/392/395/399/402 | SQL/RTE/Error | checked alias・brace無しnullguard |
| readRejected | rows | 511/518/521/525/529 | SQL/RTE/Error | 通常 |
| readRejected | statement | 504/530/533/537/541 | SQL/RTE/Error | 通常 |

CloseResource8はnonnull元資源のidentity aliasであり、未取得nullは固定SQL拒否。未知bodyの同一failureを保持し、同じowned資源を一度直接close、helperはSQL/unknown順位と固定secondaryだけを扱う。referencesのIOExceptionはSQLへ固定化されず伝播する。finallyでの条件throwは成功body/SQL primaryを未知cleanupより優先しないために必要。provider getterはpure projectionのIAE変換の外に置かれ、borrowed Connectionのclose/commit/rollback/config変更なし。用途判断としてMain変更不要、型解決/実close回数/SQL/原本/親資格は本群未検証。

元1491raw/562参照保持、既新用途48＋今回48=新用途96、用途又は参照658/当未接続・未用途881→833。raw抑制0・実適用違反数null・新PT/coverage/全F03/正式受入0。old68fault成功をIO二scopeの証明にしない。BUG/YKTは工具の有限是正/全対象予防検査まで終了、保存commit確認後に台帳へ有限完了を追記する。Production/RD/UI/SS/Test/旧成功変更0。

対象Main SHA2baed428e77bb6fee2114ecac7d66d1ee5917d45e1bc9f25beb1ac5ba7eba90d、helper f4cff9bb…、SS332 bf35de0b…、SS331 7f6e0430…を原manifestの全hashへ結合（承認origin/mainと同byte）。command=`python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg16058_cleanup_terminal_current_static_review.py`及び新版16062、失敗commandは元二工具の同entryで一度だけ。時刻精度未捕捉部分はnullとし、元tool chunkを保存した。

着手0.5/2/5共有pp cap10不変・fresh14:49used52/rem48。専有費/N/Tnull、14:49:38usage6523d87ee2a10767ca0e0b4b865c8c7a34deb7a1062f03cb3c48b30a57961925はNO_NEW_EXPLICIT_USAGE_RECORD、欠測を0補完しない。正式1964/53・歴史17/190・工数null・QA051final/451/HOLD不変更。次は同種copy残留を繰り返さないよう、既存共通化可能なmetadata工具を先行索引して、必要な内部整備又は許可whole PTへ進む。
