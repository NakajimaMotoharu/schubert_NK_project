# 192 NK-OPS-001 Cleanup子外部入口単体テスト仕様書

Program ID: NK-OPS-001/NK-BAT-001。対象: `CleanupProcessMain.main/run`、`CleanupNativePreflight.verify`。RD OPS-009/BAK-001、UI251、SS341/342/343、SSC-104/PG334。Test ID: PT-OPS-CMAIN001～004、NCLEAN001。Production入口は必須契約未結線中の非成功状態であり、親M/A・全actor終端・実DELETE/transferの合格ではない。

| ID | 事前条件・fixture／入力・操作 | 独立期待値と根拠 |
|---|---|---|
| CMAIN001 | 公開固定manifestを返すpreflight、argv空、二回呼出し | 呼出し各1回、終了30。SS341§7/SSC104でpreflightのみは0/10不可。Production結果を期待値生成に用いない |
| CMAIN002 | 任意argv二件、preflight呼出計数 | 終了70、preflight呼出0。SS343固定引数0件・秘密/任意path禁止 |
| CMAIN003 | 既知IOExceptionに非公開canary、未知Runtime identity | 既知は30/診断非露出、未知は同一identityで非正常伝播。SS333例外優先/SSC104 |
| CMAIN004 | 引数/port/結果null、host非rootでnative呼出し | nullはNPE契約違反、非rootはIOExceptionで拒否。正常値へ補完しない |
| NCLEAN001 | host UID≠0、真正systemd CLEANUP Unitなし | 固定root contextで拒否し、private credential/DB/backupへ進まない。外部成功の代用不可 |
| CUNIT001 | 固定candidate Unit template、公開文字列oracle | root oneshot・固定子entrypoint・PostgreSQL/Backup順・private request、`SuccessExitStatus`なし。SS342§4/SSC104 |
| CUNIT002 | 同Unitのcredential/environment行 | `db-batch`固定sourceとrequestの2件だけ。env/argv secret・SetCredentialなし。SS343§6/SSC104 |
| CUNIT003 | 同Unitのstop/hardening行 | Artemis前段、restartなし/自動SIGKILLなし、read-onlyの暫定入口。SS342§4/SSC104 |

追加確認: 固定credential directory、backup root/NSS、本番URL、root pre/post、4file/両DB rowと全closeの結線をcode review/静的検査で追跡する。実rootで全経路を通る試験、Unit配備、親M/A・同run handoff、DELETE/transferは後続PT必須。対象classのJava line/method/class/branch各100%を最終受入条件とする。今回のhost限定失敗経路だけでは`CleanupNativePreflight`の成功経路coverageは満たさない。範囲/環境/command/commit/結果・coverage/関連BUG/SSC/evidence path/hashは193へ記録し、未実行を合格算入しない。Secret、raw request/password、DB dumpを証跡へ保存しない。
