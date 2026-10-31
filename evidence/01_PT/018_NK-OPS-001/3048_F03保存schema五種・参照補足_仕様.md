# F03 保存schema五種・参照補足 仕様

2026-10-31 / PG-D974 / 群3383 / WBS-F03。開始0.5/1.5/3共有pp cap10固定、used50。現Main1491の3047/15930を固定し、新しいsource解析・手動レビューの出来高でなく、既存レビューへの参照不足を補う。

対象は固定PG10822 thread dispositions、PG10828 classloader dispositions、PG10810 protocol contexts、PG10726 JSON contexts、PG13044 identity reviewedRowsの公開五manifest/fileだけ。source hash、全attributes座標/ruleが現rawと一致した場合だけ追加参照。identityは固定10690の元ID/属性とAST座標も照合し、座標差は推測補正しない。未知schemaを推定変換せず、Test/旧sourceのbyte不一致/現在rawなしを対象外として数える。

原1491row/283参照/1208旧選択queueを凍結、補足JSONと新選択queueのみ生成。重複occurrenceと既存参照を消さない。新接続数を新規review・PT・適用性合格・工数消化へ算入しない。独立checkerが五input全hash/全rowと選択条件を別計算し、byte/座標/参照偽装・欠落・旧消去・適用性/動的昇格を拒否する。Product/元成功/PT/VM/DB鍵/外部/私有rawの操作なし。F03/451・正式/QA051final/HOLD不変更。
