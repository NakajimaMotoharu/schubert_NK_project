# 正式証跡manifestの形式検証

G08、関連F03/2-3、SS354、451、PT-QA-TRACE-004、BUG-3461／YKT-2763。対象 `018_collect_verified_evidence_set.load_success_manifest` は保存rootと個別scopeの両入口。オブジェクトのキーは一意、JSON標準の数値だけを許容し、終了値は整数0。run、source、branch、各SHA-256と固定53 scopeの全件検査は従来どおり。

独立試験 `EvidenceSetTest.test_manifest_json_has_unique_keys_and_integer_exit`。合成成功の一文書は許容。bool false、float 0.0、終了欄の重複、files内pathの重複、非JSONのNaNはすべて拒否。各入力のSHAを別計算で更新した上で判定し、形式の不正と内容のhash不一致を区別する。hashは製品validatorを使用せずPython標準SHA-256で計算。

PG41104の修正前は拒否期待5がすべて失敗。PG41106は新1件と既105件の工具自己試験を一回実行し全106成功。新1件の内訳は正規1と拒否5。旧の固定全53の正負とfail-fastを同一候補で維持し、保存rootも共通読取へ接続。製品PT・本物の証跡収集・正式451・既認定変更は各0。

実行 `TMPDIR=/dev/shm python3 -B tools/quality/019_test_evidence_set.py -v`、独立 `python3 -B evidence/01_PT/018_NK-OPS-001/input/5585_g08_formal_manifest_post.py`。 [初回](evidence/PG41104-g08-formal-manifest-before-v1/manifest.json) [現結果](evidence/PG41106-g08-formal-manifest-after-v1/manifest.json)
