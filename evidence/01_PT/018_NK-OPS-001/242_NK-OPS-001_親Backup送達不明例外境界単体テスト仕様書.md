# 親Backup送達不明例外境界 PT仕様（PG365、修正前）

Program NK-OPS-001、class/method `MorningBackupUnitCycle.execute`、Test ID PT-OPS-BUCYCLE-005。RD OPS-009/BAK-001、UI251、SS341§5-6/343§6.15、SSC105～107、BUG-324/YKT-256。239の補足。親のM/A/原本/DB/requestがcallback全期間所有される前提で、呼出境界で送達不明を正常解放しないことを独立して確認する。

| 入力・事前条件 | 操作 | 独立期待 |
|---|---|---|
| root/baseline事前失敗、start未呼出 | baseline captureがIOException | start0、保持port0、固定IOExceptionで安全に拒否（送達不明でない） |
| start portに入ってからIOException/StopGateException/RuntimeException/Error | 各例外を投入 | marker retire0、stop0、保持port1。外側へ通常return/checked例外でunwindしない。SS341/SSC106の「送達不明」をoracleとする |
| start portからnull attempt、attempt status/awaitからnull | nullを投入 | NPEを成功へ変換せず、同じ保持portへ入りmarker retire0。null契約は違反として扱う |

fixtureは公開合成portと保持到達用sentinel。製品methodをexpected生成へ呼ばない。実Unit/30分timeout/marker inodeの実測は別必須。REDでは既存codeの `start.execute()`境界外及びNPE未捕捉を確認し、GREEN後に関連BUCYCLE全件・Batch影響・静的/coverageを再試験する。command/環境/commit/exit/coverage/hashは243結果とsanitized manifestへ保存する。秘密・raw session/credentialは保存しない。
