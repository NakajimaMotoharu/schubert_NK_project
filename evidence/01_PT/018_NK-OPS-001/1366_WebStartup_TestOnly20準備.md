# SSC324 Test-only red20準備

全851Mainは元aedと同byte、既Main/Test/gates/Currentを変えず新WebStartupRetentionTest二method/同child Driverだけ追加。START324001の明示normal Replay→replies/nullable Replay/null boundary、START324002のdummy自己所有daemon五mode（checked/別RTE/Error/同一startup RTE/worker確認後reply checked）で正常1000ms超・割込後にも非復帰/後続非解放/一回close/外側finally0/同startup frameを観測する。busy-waitの一瞬誤判定を避け、TIMED_WAITING/frameは有限3秒pollで確認。child全20秒・失敗時このchildだけ有限cleanup、env空/専用TempDir/同run agentのみ、実runtime/provider/DB/JMS/network/Root/VM/cohort/intent/鍵/原本は無し。

新PG6360 `tools/quality/pg6360_web_startup_red.py`は元18/6350資格fb7279b4を読取再利用し、宣言20/10（子modeを5PTに増やさない）・既851Main/全他Test固定/gates/Current差0/clean commitを要求して一回だけnew namespaceへ実行する。`PYTHONPATH=tools/quality:tools/quality/vm/050_s1:/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime python3 -B tools/quality/pg6360_web_startup_red.py`。対象commitはTest保存後begin.safe.jsonで固定、まだ実行していない。二工具定義/negative/pyflakes0、正規formatterは元19555真正0（観測poll調整後の再formatは次記録）。赤の初normal nullは未実装TDD、UNKNOWNの違反は先行票BUG1574へ、未到達matrix/後moduleを成功へ算入しない。

PG案は既SSC318の保護済み有限診断/観測を共通内部factoryから取得前構築し、Web startup側がnonreturn loopと各有限interval後のreachabilityFenceを所有する。到達しない非復帰call後finallyにfenceだけを置く案は採用しない。これはSS324の保持/無後続解放/無新規割当を満たす実装詳細であり、外部仕様/旧oracleの都合変更ではない。PG後は既原oracle固定の関連54/15→必要全体へ集約、他factory/consumerの横展開未完を残す。

設計main PR186/c8488d363は公開済、正式1964/53・17/190・工数null、原-v4/開始.5/2/6保持。freshused40残60/reset1793082864/secondary不明。PGと新PT未完/実環境HOLD/PTALT不明代替0/QA051final/全保全を維持し、通常red/commitで停止しない。
