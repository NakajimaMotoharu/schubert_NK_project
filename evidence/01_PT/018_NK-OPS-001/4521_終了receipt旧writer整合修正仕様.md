# BUG3194/YKT2661 終了receipt/legacy writer adapter
ToolFix low .1/base .3/high .8 cap1。純metadataだけ。end_fieldsで既検証のreceipt/hash/postterminal/window比較を保全し、旧writerへ渡すbefore/after primaryをflatへ写す。既存end_fields契約とcanonical marker guardは変えない。新adapterは不一致receipt/負差/窓長/marker/欠測/型をfailclosed又はunknownとして保持。synthetic純工具testでAPI/resetを実行しない。
既存END8件はorigin eventsをread-onlyで照合し、同一receipt/marker/窓/非負差が確かめられる分だけ別eventへ追記訂正。旧events/原価格/配賦/受入/実token不明を変更しない。共有coarse0ppは消費token0/専有0/無料の証拠ではない。新しいSource/製品試験/VM/DB/Root/cohort/四held/鍵は一切関係しない。
