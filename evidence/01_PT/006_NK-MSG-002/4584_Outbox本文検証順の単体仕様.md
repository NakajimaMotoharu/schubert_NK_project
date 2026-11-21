# Outbox本文の検証順と所有の単体仕様

WBS-P018-10.03/2、参照WBS-P004-05/2、SS324・351。BUG-3489／YKT-2782。対象はOutboxRequest／OutboxEntryの全引数constructorとbodyアクセサ。借用byte配列の内容は参照時に検証せず、長さと非本文の不変条件を先に確認する。

| Test ID | 合成前提・操作 | 独立期待 |
|---|---|---|
| PT-OUTBOX-COPY001 | requestの本文空とDLQ metadata欠落、次に本文 `09 02 03` とmetadata欠落 | 空の固定例外を先に返す。非空はprofile不一致固定例外。借用本文は同じ3 bytes |
| PT-OUTBOX-COPY002 | entryのlease owner空とDLQ metadata欠落、次に正常ownerとmetadata欠落 | owner固定例外が先、次の呼出ではprofile不一致。借用本文は同じ3 bytes |

元OutboxModelTest4／OutboxDlqMetadataTest2／OutboxRetainedValueContractTest2を再資格する。合計予定10。正常時は元caseの独立literalと、入力・accessor配列を変更しても保持済み本文が同じことを引き続き確認。静的期待は両constructorの全検証とprofile確定の後に、clone一回を行い、保持fieldへ一度格納して返ること。失敗確認に実OOM・実本文は使用しない。SQL/JMS/配備/実ログは別契約。
