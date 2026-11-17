# Outbox保存値と宛先 単体テスト仕様

WBS-P006-02/P018-10.03 CATALOG-022/023/F03、SS312/331/351と451、PT-OUTBOX-VALUE-RAW、BUG-3218、YKT-2431。旧OutboxModelのwhole4、旧OutboxDlqMetadataのwhole2に変更を加えない。追加は次の合成2件。

- 宛先はSSの固定二名称と二address、返却配列の独立性、null・未登録・不正enum名の拒否を確認。
- 保存値と送信要求は既定non-DLQでOptionalが空、入力後の配列変更・取り出した配列変更によって値が変化しない。固定診断は許容されたID／宛先のみで、本文や個別識別子の出力がない。

実送信、broker、DB、権限、native、鍵は試験に含めない。元PT成功へ合算せず、現source実行、独立XML/CRC、対象三classの全Codeと四counterを報告する。PG38276以降。
