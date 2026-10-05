# NK-OPS-001 Caddy reload履歴境界 単体テスト仕様書

Program/class/method：MorningCaddyReadiness.cold/coldInvocation、関連MorningStartupLaunchOwner.publishCompleted・fixedstart gate。RD OPS009/DAT009/BAK001、UI251、SS342343353、SSC180191192、QA047、BUG730/YKT517。実結果343、safe manifestのTest ID・source hashへ追跡する。

| Test ID | 入力・操作/事前条件 | 独立期待値と根拠 |
|---|---|---|
| CADDY192001 | 手書き正常停止F18：inactive/dead/PID0/Job空/success/Code1/status0/非zero32hex/start1000000/exit2000000。固定validate/run補助entryを両exact n/a/pid0/code(null)/status0/0へ置く | SS342 SSC192により返すのは旧Invocation literalのみ。旧世代readyはIOException、新世代の別literalの真正active profileはready true。Productionでexpectedを生成しない |
| CADDY192002 | 片側だけ正常→未実行、path/tmp/ignore_errorsyes/pid1/codeexited/status1/time改変を各補助entryに独立適用 | 全件IOException、n/aはvalidate成功/新ready/旧close権限でない。片側混合や改変から正常履歴を推定しない |
| CADDY192003 | 両補助unusedのまま、F18 failed/running/PID/Job/Result/Code/status/start0/exit逆転/zeroInv/foreignId/rootUser/NNPno/欠落exitを適用 | 全件IOException、正常F18と固定profileの条件を維持。既存null/missing/uint64/pid境界・owner/io故障は同suiteで再試験、NPEをcatchして正常化しない |
| PT-OPS-RET468001 | current37599b0d/旧32record＋current4/current1＋3intentの独立集合40、手書きfull18/launch/原本341行14列、実capture/watch | 旧世代混同/欠落/余剰/順序飛越/逆行/所有close故障を拒否。既存RootFailedStartRecoveryのtyped逆順退役後37recordを保持、新permit/start/DDL/原本変更0。Pair422/actualpeer14工具assertはProduction PTへ加算しない |
| PT-OPS-CADDY192004 | source固定fresh全6→正規署名同byte→現在failed cohort新M/A/DB所有隔離/退役→新Morning一回 | 全XML/FES0/静的全6/source前後hashを照合。そのsourceで真正Root→ordinary API/Web/Caddy/TLS/原本DONE/intent全退役/全通常返却まで実証する。旧df9親30/PG464 A01を補完流用しない |

実行command：`pg468_caddy_selected_v1.sh`、`pg468_recovery_compile_v2.sh`、保存HEADを渡す`pg468_full_v1.sh`。JDK25.0.4/Maven3.9.12/Node24.19.0/JaCoCo0.8.15/PG18.6隔離VM。Inputは同test literal・current失敗cohortのroot私有原本（Git非格納）。限定cold counterの100%とglobal/native100は別判定。並行/再送は既存owner/launch/DB/budget影響suiteとfullで確認、再startを同失敗runへ二重発行しない。

仕様期待値・実際値・実日時/終了code/source/branch/environment/coverage/BUG/SSC/証跡hashは343とsafe manifestへ保存し、failed/skipped/not-run/別sourceを合格へ加算しない。
