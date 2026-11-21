# Outbox本文の検証順と二つの既存期待値の結果

WBS-P018-10.03/2。P004-05/2は共有証拠のみ。仕様4584、SSC-464、SS324・351。BUG-3489/YKT-2782。PG41398は旧classに現入力が一致せず解析前停止。PG41400で当二型ともDLQ profile確定より前にcloneすることを現sourceから確認。2611e1acbdで各constructorの検証後、最後の一度だけ本文を取得する。

PG41402は真正終了1。10中8成功・旧OutboxModelTest二件が旧診断を要求。BUG-3490／YKT-2783を先に登録し、6cd4741404で承認済みSS351の完全固定文へ期待値を適合。二箇所と不要importのみ。元失敗XMLとexec指紋を保存。製品Mainは再compileせず同一入力・元出力を再利用。

PG41404は元八と新二の10件、F/E/skip/not-run各0。PG41406は独立XML・真正一exec・CRC7、SpotBugs scope8と指摘0、PMD／Checkstyle／format各0。計測toolの初回事前照合は全488実行レコードと製品7を区別する前に停止した。JUnit・Mainの再起動なし。元失敗execとの合成なし。

| Class | Line | Method | Class | Branch |
|---|---:|---:|---:|---:|
| OutboxEntry | 52/ 52 | 19/ 19 | 1/ 1 | 18/ 18 |
| OutboxRequest | 28/ 28 | 12/ 12 | 1/ 1 | 2/ 2 |

実JMS/DB/診断sink、全F03／451は未受入。

- evidence/01_PT/018_NK-OPS-001/evidence/PG41402-outbox-copy-after-validation-v1/failure.json SHA-256 8e4a836a8f33f33b5269f492eb0f15b75c7dabe1ca8bc29d61be3e9a29f19d58
- evidence/01_PT/018_NK-OPS-001/evidence/PG41404-outbox-copy-and-approved-fixture-v1/manifest.json SHA-256 6d12c9cfe85032811d42a8114ab892ae7b160afba6685a78fdbee277fdc52737
- evidence/01_PT/018_NK-OPS-001/evidence/PG41406-outbox-copy-independent-v1/manifest.json SHA-256 3fc26d3d1dc25f78447530249dc2076ffe0d4bab6f668f7ed20596e25881b44c
