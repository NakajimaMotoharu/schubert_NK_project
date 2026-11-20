# F02 API repositoryの受信層への依存

WBS-F02-a実行計画行9、NK-OPS-001、SS311 §3、PG-D516、BUG-3462／YKT-2764。入場条件は承認済み設計と対象sourceの照合。独立期待値はSS311のAPI依存方向であり、実装の判定関数から生成しない。

| Test ID末尾（PT-F02-REPO-INBOUND-） | 合成fixture | 独立期待値 |
|---|---|---|
| 001 | persistence型の受信portフィールド | 逆依存1 |
| 002 | monitoring.persistenceから受信port呼出 | 逆依存1 |
| 003 | Repository命名型に属する内部class | 逆依存1 |
| 004 | 受信portの二次元配列 | 要素型への逆依存1 |
| 005 | applicationからpersistence | 指摘0 |
| 006 | persistenceのdomain値参照 | 指摘0 |
| 007 | persistenceのoutgoing port参照 | 指摘0 |

OpenJDK25／ArchUnit1.4.2。六自己所有JARはコンパイルのみ。実行は静的工具と独立の証跡読取のみ。製品JAR・サービス・DB・MQ・固定試験の追加実行なし。既存103条件は4件の是正対象による副作用の確認で、再資格や個別受入に加算しない。

`PYTHONDONTWRITEBYTECODE=1 python3 evidence/01_PT/018_NK-OPS-001/input/5586_f02_repository_inbound.py before|after` と独立 `5587_f02_repository_inbound_independent.py`。Core `559f5b5945e82374e0843dcfae11a8d07faef1ea`。詳細な工具source、終了値、raw output SHA-256、各入力と結果は各manifestに記録。

- [PG41110 修正前](evidence/PG41110-f02-repository-inbound-before-v1/manifest.json) は3/7、未検出4。元の指摘67を保存。
- [PG41112 修正後](evidence/PG41112-f02-repository-inbound-after-v1/manifest.json) は7/7、前後とも166物理、既103・既指摘67を保持して今回期待の4指摘だけ増加。
- [PG41114 独立照合](evidence/PG41114-f02-repository-inbound-independent-v1/manifest.json) で指摘集合の差と現API repository関連16 sourceの受信名0を照合。実API・Web JARのbuild、物理境界、署名、451は継続。
