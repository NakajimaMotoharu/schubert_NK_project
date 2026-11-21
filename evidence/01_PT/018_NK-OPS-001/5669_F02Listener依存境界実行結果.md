# 5669 F02 Listenerの直接JDBC・file境界の結果

WBS-F02-b、SS311 §3／§10、BUG-3488／YKT-2781、仕様5668。PG41388で期待違反6の見落としを確認。修正07bdd251daではJMS入口とAPI inbound Listenerの直接JDBC・file操作・Storage依存を既FRAMEWORK_FENCESへ追加。合成上で許可したJMS型、file/JDBC adapterと非JMS callbackを区別。

PG41390 新規合成10の期待すべて一致、元53合成の期待検出29も維持。PG41392で報告の5規則、旧29と新6の完全集合・重複0、現入口5のsource SHAと明示参照の字句確認を独立照合。製品classfile、実Listener、業務transaction、DB/JMS、実ファイルの実行は0件。

- evidence/01_PT/018_NK-OPS-001/evidence/PG41390-f02-listener-owner-green-v1/manifest.json SHA-256 bb782a7aba82f7fbe75bf30ee6990b1b762abe7df564f175f07ff3d34c028395
- evidence/01_PT/018_NK-OPS-001/evidence/PG41392-f02-listener-owner-independent-v1/manifest.json SHA-256 1784590c6883356c24ca6f690bd4ee3afd5e80eb4d66249df9ed8a75a2692001
