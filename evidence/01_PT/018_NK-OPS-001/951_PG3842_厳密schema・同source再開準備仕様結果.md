# PG3842 厳密schemaと同source再開準備（限定、未正式）

Program NK-OPS-001 / current_after_native_schema.expand、pg3842.payload、pg3844.sources、pg3848/3850。SS343 6.13/SS353/354、451。Production 7fffab57a567914956b66452e5e54388642efdec／PG3748。BUG1326/YKT1092、QA051final保留。

| Test ID | 入力・操作・独立期待値 | 実結果/証跡 |
|---|---|---|
| PT-CURRENT-FULL11-3840 | 停止afterの厳密schemaを読取、nativeを別provenanceで照合 | 旧11前提でactual1、Ref/DB/SAVE前。元失敗保存、合格加算0 |
| PT-CURRENT-SCHEMA-3842 | exact10、元34before、selected10/除外30、実40execのhash/metadataと独立集合一致。欠落/余分/type/path/hash負例 | pure1成功、旧after書換0 |
| PT-CURRENT-FULL11-3842 | 同source187、24表二読、十Unit18/32設定/元journal、原本117/Backup47/鍵19/旧proof51/native40、資源0、fresh十Ref正常返却 | 実0、01:49:05～14Z、before3459bd3d705f463c006b0bb3ffafb47ea7896c5c226f3f067e18600dd1e9aec3 |
| PT-CURRENT-RESUME-ABI-3846 | 20source固定/現在Root positive tupleのみ結合、negative fixture維持、全Java lintWerror及び独立5main | 六phase全0、01:53:26～28Z、pg3846-frozen-v1.safe.json |
| PT-CURRENT-RESUME-BOUND-3848 | 閉じたstage/prepare二操作、新only予約/実frozen hash/clean固定/一gate、独立literal差分/全11照合/旧journal/Ref返却 | pure2成功、実stage/prepare/postは未発行 |

実行環境Linux/JDK25.0.4/Python3、PYTHONPATH=tools/quality:tools/quality/vm/050_s1:toolchain/pyflakes-3.4.0/runtime。命令 `python3 -B tools/quality/pg3848_current_resume_dispatch_test.py`、2tests/0failure/error/skip、2管理試験でProduction3714へ加算0。3842 payloadSHA f417aa08758d1cf8fc950ae51acb2a9520e6f50dbec038e7a14b864b54b8a619。元manifest/時刻/command/exit/version/sourceは私有PG379の各runへ保全。native・DB全値・鍵・認証/session等のGit格納0。

独立期待値は承認済みsingle-drop-in literal、元24表・metadata/hash・selected/excluded閉集合及び固定negative fixture。Production methodからexpected生成0。coverage100/F03/CHR/451/工程完了は未認定。新resumeはまだ未実施、同run/cutoffでも新activation/新一回用権限を必要とし旧ownerを移植しない。

## 実consumer追補（2026-10-16）

3848stage0/prepare0、operator7ffda5586、01:59:44～02:00:43Z。一normal runtime reload、SQL/start/stop0。3850独立post0（02:01:03～13Z）全11/実native40/全24二読/Unit18/config32/元journal/187・原本Backup鍵旧proof・資源0/全十Ref返却。preparedAfter2324d231f50b81cebef61434ffeec56e00db3f9a9ac2c26538ab07ff8642925d、payload47a5955d49a52b61f814a3617c563c0bc067d7ea51d808d6d07a4523c8fca7ac。BUG1326/YKT1092有限consumer完了。

PT-CURRENT-RESUME-ADMISSION-3854：新observer/one durable guard→start順序、全40生native先行コピー、新runではなく同run/cutoff・別activation、Browser readiness入力/class hash不変、独立pure4成功。新Root発行/真正終端/後続nativeは未実施なので未合格。管理pureをProduction件数へ加算しない。
