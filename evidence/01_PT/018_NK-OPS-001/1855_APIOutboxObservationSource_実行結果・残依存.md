# API Outbox観測source cache・限定実行結果

2026-10-25/PG-D631/group2086、1854と同範囲。Production source `2ed81b14bb41512e1cda720a446ed7b261121605`、未配備。開始低2/基準5/高9pp/cap10、共有used52→52（丸め差0、専有費0を意味しない）、実token/N/T/工数null。元/v4/v5は不変更。

| 段階 | 正本manifest（evidence/provisional配下） | SHA256/結果 |
|---|---|---|
| normal六module | PG9042-api-outbox-source-six-compile-v1/manifest.json | 8680b2ac1059c8acb365d32f48f984124b13d6aeefa0632a6f9a546360290397 / exit0・試験0、NullAway/compiler合格 |
| 元普通JVM | PG9044-api-outbox-source-host-v1/manifest.json | 807a12324f097a15af1a89c73394cedd1c6e4842ed7767ae6bf6fe5502339712 / actual36・2suite・F/E/S/aborted/not-run0 |
| private lock個別判断 | PG9045-api-outbox-source-lock-review-v1/manifest.json | 5b5d57924ade2b358cc0f7e3d6e5457ec3dd5346fb6392691e31afb86adf4451 / 当source/411/元XMLの017-020等と結合、次postで実raw一致 |
| 同source独立post | PG9046-api-outbox-source-post-v1/manifest.json | d188fc8a7b0261a0e187d2aeda5f56af783db22f1b7fdcb4f6525685c6d69f14 / L25 M5 C2 B7 missed全0・CRC0/session1 |
| 全byte/所有/architecture | PG9048-api-outbox-source-trace-v1/manifest.json | 9674bdaea983763fa6c5615ee747657f8bed9cebeeb0a91a0f36ce114ef44ed3 / 全1838Main・既1836同byte・新outer/Entry二・237source owner・5rule違反0 |

OUTBOXSOURCE001～020新20、既APISERVICE001～016を必要回帰16、fixture outer二classはcompile-onlyでPASS加点0。手書き3/5/7と2/4/6秒、SQL後条件・固定wireを独立期待とし、constructor/null/mode、正常empty既知0/未供給NaN、更新、SQLException/Runtime/Error、RS/PS close順・同primary/secondary、inflight missing二回のABA防止、writer直列、SQLなしサービスrenderを検証した。JUnit原XML・exec・環境・command・source/hash・終了code・入力sourceはhost manifestと元runに結合。実行は `PYTHONPATH=tools/quality:tools/quality/vm/050_s1:/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime python3 -B tools/quality/pg9042_api_outbox_source_six_compile.py`、9044/9045/9046/9048も各同環境・先行pyflakes0＋set-e。成功済みnew-only工具を再実行しない。

二Main全体をcoverage対象とし、Entryはbytecodeに条件命令なし・実branch0/0=NA（除外/偽100なし）、outerの実branch7とaggregate四100を分離して確認。Checkstyle0/SpotBugs0、PMD生1/exit4はprivate writer lockの個別必要契約として当source/元XML/411と結合し未分類0。生PMD0や全F03合格とは呼ばない。traceにはprotocol5＋不正post6反例、postには7receipt反例があり、旧helperのvacuous branch拒否を一律緩和せず当Entryだけの物理根拠を検証する。

環境/工具作成失敗を別記：9042最初のimportはPYTHONPATHから既設pyflakes runtimeが欠落しexit1、stage.main前で製品job0。9046作成時のJS置換文字列展開でpreflight SyntaxError二回、analysis/job開始前でfail-fastし、明示apply_patchで初回実行前に是正。元記録は各 `PG9042-import-environment-failed-v1` と `PG9046-tool-construction-preflight-v1`。製品試験失敗/新BUGではなく工具構築・実行環境手戻りとして費用を分離する。成功した36件やnormalを確認目的で反復0。

残：actual-owned RO producer/接続取得・transaction設定・有限停止/Pool寿命・clock/采時・poll周期/期限の根拠、API callerへの実供給は未接続でHOLD。default API sourceは引き続きOptional.empty六NaN。cacheはSDKを参照しないのでlate producerが閉鎖SDKへ触れないが、それを実Pool/停止成功へ推定しない。実DB/VM/Root/cohort/native/intent/permit/配置等HOLD、current all-source/native/CHR/四100・451・QA051 final/G07未分類8379・正式1964PT/53scope/原190新受入0/工数nullを維持。技術新20ID/二Mainのみ加算（累計690ID/37Main、異sourceを全体資格へ合算0）。関連新製品BUGなし。保全・計測・push後、当producerの既承認SS/現artifactによる着手依存を限定照合し、許可済みPG/PTへ通常継続する。
