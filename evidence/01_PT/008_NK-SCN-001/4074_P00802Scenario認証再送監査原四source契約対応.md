# P00802 Scenario認証・snapshot/replay・監査 原4source

FUN003～005/FIL001～009、UI223/224/234/237、origin/main SS312/324 §6.3/7.1。対象method・独立期待値・TestID・全source hashは[PG26838](../018_NK-OPS-001/evidence/PG26838-scenario-replay-contract-v1/manifest.json) checksへ対応。全4 source読取済み。

PT-SCN010～014/009-S01～S06: readonly新鮮actor・Inbox参照→TX外file準備→write新鮮同owner・Inbox排他、NEWだけsnapshot/criticalaudit確定、再送で業務/audit重複無し。復号全header/length/semantic/state/ref/時刻/ownerを検査、初回0000/確定9001・SCN0104のみ保存、成功再送0200/失敗元code、fresh Message/時刻/context、buffer消去。file置換は同content/元metadata維持・CAS別gate。PT-SCN-AUD469003～006: search総件数/detail INLINE件数・FILE件数、借用接続/所有statement、NFC改行制御文字redaction、JSON layout/resultCountだけ、SQL exactly1。

BUG2679/YKT2359: Replay六catchで元fatal graphを検査せず固定例外へ変換。SS312既契約内の不備、修正前原状は同directory fatal-conversion-before.json。source修正と静的reviewは別事前価格、runtime/PTはactual4 HOLD。DB全fixtureやAudit5の部分抽出で迂回しない。Audit5 sourceは全文、他whole2は依存/メソッド索引までで試験body全文監査とはしない。

metadata command `python3 -B evidence/01_PT/018_NK-OPS-001/input/1355_scenario_replay_contract_audit.py` exit0、新規PT/coverage/元190受入0。原/1準備だけ完了、/2はBUG/actual4・DB・終了依存・451未受入。正式1964PT/53scope・工数null。

PG追記: source 820d932442801a8f398fb59ad32d6d737a23f725でfatal共有port六接続、PG26846 format/Checkstyle0、[PG26850独立source照合](../018_NK-OPS-001/evidence/PG26850-scenario-fatal-source-independent-v1/manifest.json)。実PT/coverage/NullAway/SB/PMD未実施、BUG2679/YKT2359 OPENを維持。代替静的結果をPT PASSへ混ぜない。
