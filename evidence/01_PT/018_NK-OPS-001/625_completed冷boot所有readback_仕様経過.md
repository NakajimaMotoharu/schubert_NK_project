# PG1023～1025 completed冷boot所有readback（準備の前段）

Program NK-OPS-001 / WBS-N11、SSC243/SS343/353/451。Production current40ef/PG932/BOMb75e/187/schema028、新bootcbca、原本eeae/091663ce/cutoff2026-10-09T23:31:22.087768Z/DONE23:56:48.112404Z。完全completed・active無し、startup/PT-native無しを保持する。新candidate d5b001042は未配備で別管理、既signed sourceへ巻き戻す操作ではない。

| Test ID | 入力・独立期待値 | 状態 |
|---|---|---|
| PT-DEP-1023001 | 固定verifyのみ許可、null/欠落/未知/prepare/execute/余分拒否、手書き元原本三tuple | Java oracle PASS |
| PT-DEP-1023002 | 両M/A kernel lockが同Java parent・各一件、片方欠落/重複/外国PID/READ/blocked/inode alias/nullを拒否 | Python独立golden PASS |
| PT-DEP-1023003 | 専用RO schubert_batch・advisory71419602・同backend/application、実server heartbeat、active/idleの正常pulse競合、DBclose後実peer/advisory0 | 実VM未実行 |
| PT-DEP-1023004 | tenRef/heldrun-originalFD、完成原本二読、独立1004/1005sealed全24-594/全10cold32/Backup47/credential19/original59/旧proof28/署名187原値不変更 | 実VM未実行 |
| PT-DEP-1023005 | DBrollback-close-confirmed→server0→Ref-bus-FD→originalSession/A/M正常close、新only complete、unknownは隔離保有/成功認定0 | 実VM未実行 |

工具の独立6Python unittest（複数反例subcase）＋Java引数/golden、compile`-Xlint:all -Werror`は実0（PG1024）。正常・null・境界・故障・lock競合のexpectationは手書きLinux kernel行・元原本固定tuple・独立private before hashを使用。DB後条件はProduction expected生成でなく、保全済み全24row fixtureとの不変比較・専用server実問合せで検証する。Java同接続が実transaction_read_only/current_user/session_user/backend/application/lockを検証する。固定application alias PG243-cold-emptyは既797の3桁grammarを維持しSSC243を表す、operator/source/run PG1023～1025とは別field。

新helperの`prepare`/`run`通信はreadonly pre/post観測であり、旧983のUnit実行ではない。旧ISSUED-original verify/旧Unit actionを呼ばない。parentに新M/A、専用RODB、その下に十Ref/保持FDを接続。rootの新私有receipt以外のdir・epoch・mount・DBrow・credential・Backup・原本・config・Unitへのwrite0。close未知・EOF・owner失効は非成功/隔離保有とし、古い正常終了やcoldによる成功を推定しない。

Host `python3 -B tools/quality/vm/050_s1/pg1024_cold_readback_compile.py` source5a8aacfc8/2026-10-10T05:14:14.212850～05:14:15.453769Z、終了0、97helperclass/frozenSHA0dd14dceccd3a199e3021ffed4d6adde7282b767db7cbcb2af02a46bb004d175。Java25.0.4/Linux/Maven3.9.12既toolchain、Production PT加算0（工程工具試験）。Python transport二case実0。

Stage `python3 -B tools/quality/vm/050_s1/pg1025_cold_owned_native.py stage` source5e721faf9/2026-10-10T05:19:59.272717～05:19:59.633562Z、終了0/logSHA8cb53b97f88909e33d0cb228ef4a77b1dfad9d1835c29a64f5c805d7bf0929e7、guest新onlyRoot0700/全file0400/hash/sync/boot/current確認。stage再発行禁止。

次`python3 -B tools/quality/vm/050_s1/pg1025_cold_owned_native.py verify`を新only予約一回で実行し同jobへ再付着。成功後も準備完了ではない：hostRO、空4namespace/16PT-native dir、独立post・正常scopeの実prepareを後続で閉じる。実readback後の結果/source/job/exit/hashを追記し、live retainerがあるなら所有を勝手に解放しない。旧source native10/正式24-1964-53は不変更、IT/ST受入0。
