# 修正marker実RO・独立全後条件

NK-OPS-001、SS343/353/355、SSC283、BUG1184/YKT952、717仕様。operator/source固定88fec2dcfa433b9a380d02ff4353f69975357568、candidate0fd734195b4d5338f6b7e860e087cce561d49562、実current2741c4546afad6c1e8b6efbd53dfb58144edf7bb。正式1964PT/53scope/wholeleaf増分0。環境は既存隔離VM・JDK25.0.4/Python3.14.4、host生成pyflakes3.4.0、全source不変。

- PT-OPS-PG1873-ABI001：`PYTHONPATH=tools/quality:tools/quality/vm/050_s1:/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime python3 -B tools/quality/pg1873_warning_ro_marker_compile.py`。22:38:25.175629Z～22:38:26.519955Z、actual0。compile-Werror/argument/labelmount/original/identity/inputの全6phase0。旧1870失敗slotを再送・hotpatchしない。
- PT-OPS-PG1875-STAGE001：同環境 `python3 -B tools/quality/pg1875_warning_ro_marker_dispatch.py stage`。22:41:14.674174Z～22:41:17.284946Z、actual0/sourceQualifiedtrue、logSHA6db9cef499c3ce22a7034829749513286d641834982eafbb3ebce7df8d325446。固定全helperをnew-only配置。
- PT-OPS-PG1875-PRE001/RO001：同driver `prepare-ro`。22:41:23.419025Z～22:42:06.524333Z、actual0/sourceQualifiedtrue、logSHA018d206ad4d10cd3232404d936add3a6b32a85acee022c3ba3daf3555f31ed2e。実producer exact `PG1872_INPUT_CLOSURE_READY`＋LF/stderr空/exit0を所有前に独立literalで検証。管理owner全期間保持、候補だけhostRO化、current/approval/epoch/Unit/SQL/start-stop-reload変更0。
- PT-OPS-PG1876-POST001：同環境 `python3 -B tools/quality/pg1876_warning_ro_marker_post.py`。22:42:09.998479Z～22:42:17.321082Z、actual0、payloadSHA83802813ac6fedde902c274918e8609a6011629dddfc6c108cba67cab8811a60。独立全後条件でPID1と同mount namespace/候補mount roかつrw無し、候補187/SUMS/公開署名/source/BOM ee75d0cd61457462eca59e67f5af2d8e677427071514940f3fb594ba93a026d7を照合。旧signed187/全24row・原本Backup/全native26保持、十Unit/kernel/actor/client-advisory-flock0、新scope正常返却、旧Root13真正WARNINGとmanagerfailed10不変更。

私有manifestは`/home/mini/codex/project1/work/pgpt-runs/PG379/pg1873-frozen-v1.safe.json`、`pg1875-{stage,prepare-ro}-v1.safe.json`、`pg1875-actual-marker-prequal-v1.safe.json`、`pg1876-warning-candidate-ro-post-v1/manifest.safe.json`。raw電文/DB/credential/key/logは公開しない。input/expectedは717独立固定marker・SS正規旧WARNING/新candidate役割と全署名/BOM、actualは上記private manifestへ一意対応。

BUG1184/YKT952の当marker原因は修正実再試験と別全postで閉鎖。candidateまだunused/current未切替、Morning通常Unitまだ旧SuccessExitStatus空、reload未実行、次合法WARNING/native/CHR/四counter100/451正式品質未完。限定RO成果を全工程完成へ加算しない。
