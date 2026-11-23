# 共有利用枠のCodex識別 PT

487、WBS-G09、BUG-3678／YKT-2891、QUOTA-GUARD011～013。別製品／不明識別のtop-levelと、不成立／空／矛盾するCodex keyの5形はprimary不明かつ新規着手不成立。真正のCodex key、又は明示Codex top-levelは有効。保存済みschemaと過去開始・終端の属性は維持する。

`PYTHONPATH=tools/quality:tools/quality/vm/050_s1 python3 -B -m unittest discover -s tools/quality/tests -p 'test_pmo_quota_binding*.py'`。修正前5 subcase不一致、修正後22成功。実ツールのCodex週次残44%を正規schemaで照合した。停止閾値と料金・券に変更なし。製品PT加算0。[証跡](evidence/PG43164-g09-codex-quota-bucket-identity-v1/manifest.json)。
