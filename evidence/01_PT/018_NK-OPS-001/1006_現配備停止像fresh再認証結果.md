# 現配備停止像fresh再認証結果

1005 / PT-OPS-SSC299-CURRENT、SS343/353/354、NK-OPS-001。Source964e96e45bb588e7e75798b5adf425cbd9985427/PG4432/BOM93807abdd4db24ad300b93d95d844ea21e64487dc5cf24b815c15db34305d3de。候補825eの配備/native資格ではない。

2026-10-17 06:00:45.927494JST、元exec94551 **actual0**。operator **db1dadb3c**（remote保存確認後）、Linux/Python3.14.4、固定guest boot79a3260a-e16d-42bf-942a-b914ed144c28、host/QEMU/forwardは05:55:22JST read0。command=`PYTHONPATH=tools/quality:tools/quality/vm/050_s1:<pyflakes3.4.0/runtime> python3 -B tools/quality/pg4704_current_preservation_readonly.py`。

| 期待値（元normal停止像/署名/独立後条件） | 実際値 |
|---|---|
| 全24表を元停止像と二度比較、client/advisory/M-A/startup lock0 | 全一致/0 |
| 十Unit kernel/Job空、旧actor全消失、元正規四stop/八terminal receipt確認 | 全一致 |
| 署名187byte/32設定/原本128・Backup47・durable二分類/全runtime・startup不変 | 全一致 |
| native64物理file metadata/hash二読安定、旧streamを候補へ輸入しない | 64/安定、candidate credit=false |
| active不在・start.intent0、runtimeはdirectory二件だけ | 対象設定file0、退役操作非該当 |
| 新data-only before10/native付き11を0600私有保存・fsync | 下記hash、raw export=false |
| start/stop/reload/SQL writeなし、新起動authorityなし | 0、dataOnlyNotRuntimeAuthority=true |

元sealed after/新before SHA **612beec0ca58fcf4ecc7a15e21f4dfedd574608ba3ce947d20c6d3be728d3b90**、native付き11 SHA **5f4800ac6bb4e957db4dde31e60448433dece666788669fb6911ecca1a0615b3**。原像はguest `/var/lib/pgpt-s1-preservation/pg4704-current-preservation-readonly-v1/`に私有保持、GitへDB/原本/raw native/session/credentialは格納しない。

host証跡=`PG379/pg4704-current-preservation-readonly-v1`。元manifest SHA **fac4bfe5e0ee131860ceb6af16d1f79906523ea398d37facbd11e3d8350a8205**、payload SHA **c981b128062fa9b446ff1782acea99dcce32098faa9c7e47ac4938c37b0aa98a**、actualExit0/全safe結果・元proof hashes保存。元4658を再認定/再停止せず、新候補に先立つ現在のdata-only照合として実施した。

正式1964PT/53scope・旧17履歴・工数null・QA051final/F03/四counter100/新825e実経路は未完。PG4694全体3739/549/1646はこの時点で稼働中、別成果を算術加算しない。
