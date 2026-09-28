# 202 NK-OPS-001 Morning外部入口候補・単体テスト仕様書

Program ID NK-OPS-001。対象`MorningProcessMain.main/run`、`MorningRootScope.execute`、`schubert-nk-morning-controller.service.template`。RD OPS-009、UI251、SS341/342/343、SSC-100～102、PG339。現段階は真正root/M/固定8 policyのread-only preflight後も必ず失敗30の候補であり、実停止・A/permit/backup/cleanupを始めない。正式Unitとしてinstall/enableせず、実VMで別process安全拒否を測る。

| Test ID | 事前条件・fixture、入力/操作 | 独立期待値 |
|---|---|---|
| PT-OPS-MMAIN001 | 空argv、注入admission成功1回 | 保守全工程未接続のためexit30。preflight成功を0/10へ変更しない |
| PT-OPS-MMAIN002 | argvに任意`--run-id`/空文字、admission spy | exit70、admission0回。引数でrun/release/lockを選べない |
| PT-OPS-MMAIN003 | admissionの既知IOException/固定StopGateException | raw causeを出力せずexit30。SS341安全判定失敗の非成功 |
| PT-OPS-MMAIN004 | 未知Runtime、args/admission null | 未知は同identity伝播、nullは契約違反でNPE。NPE catch正常化なし |
| PT-OPS-MMAIN005 | reflectionで公開main/private constructorを確認 | 別の実行設定constructorを公開しない。別processのstdout/stderr/exitは実VMで独立測定 |
| PT-OPS-MUNIT001 | 固定候補Unit literal | `Type=simple`/root/PG依存、真Java main、`SuccessExitStatus`なし。SS341固定主体を根拠とする |
| PT-OPS-MUNIT002 | 候補Unitの秘密・任意入力箇所を探索 | `EnvironmentFile`/`LoadCredential`/`SetCredential`/`ExecStartPre`/RW例外0。read-only候補の範囲外を持たない |
| PT-OPS-MUNIT003 | UnitのBefore/restart/kill/hardening literal | 7後続対象より前、Restart=no、SendSIGKILL=no、30min/60sとroot hardening。実効systemd policyとは別 |

ExpectedはSS341/342の固定actor・非成功30とunit literalから作り、Production methodでexpectedを生成しない。正常入力でも非成功、引数境界、既知/未知例外、null、外部process異常を検証し、既存MROOT/MCLIENT競合・並行・再実行試験へ紐付ける。実root Unitでの成功0/10、正式8 Unit配置、A/INVALID/backup/Cleanup/permit、Artemis→API/Web、CHR-A01/L01は本候補で達成しない。JaCoCo除外なし。実行時刻/環境/commit/command、PT F/E/S、静的、4coverage、sanitized証跡/hashは203へ記録する。
