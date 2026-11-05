# F03 API三consumer七二のsourceレビュー仕様

NK-OPS-001/F03、Main28af、911の原.5/2/4pp cap5 ordinary。RD MQ003004005008010/OPS009、UI212231、SS311/321/343と各Main JMS013等既traceへ追跡する。

PT-OPS-JMS72-001: Question/Sync/WebLog各24、計72raw。型分岐23は通知/起動/cleanupの同時保持failureとdirectError優先、GC39はpartial ownership/required cleanup・登録API halt-notify/confirmed rollback、resource7はowner alias/Context所有consumer、privatefinal monitor3はclose phase直列化という各個別理由へ結合する。三class全文を確認し、graph helperやJMS providerは呼ばない。
PT-OPS-JMS72-002: SS32114のSync全close試行/遅延graph・UNKNOWN引渡しと、21のAPI通知正常return後のfatal非再throwを区別する。onUnconfirmed非帰還を正常closeへ変換せず、callbackが正常returnする場合の後続選択だけsourceで評価する。sameThrowable/通知failure/一回rollback/confirmed phase/partial acquisition/lock終了は動的未証明。
PT-OPS-JMS72-003: Context内consumer所有の根拠は [Jakarta Messaging 3.1 §6.1.8/6.2.15](https://jakarta.ee/specifications/messaging/3.1/jakarta-messaging-spec-3.1.html)。仕様上の所有責務と実providerの正常closeを区別し、共有connection全終了を推定しない。実JMS API3.1.0 jarのhashは032/既normal入力checkで固定する。新network/provider実行なし。
PT-OPS-JMS72-004: 原1491を前618+新72+残801へ独立完全partition、全raw/ordinal/ID/source/SS原文hash/unique1439/duplicate52組保持。追加で各class直前24=今回24+残0、Morning12=今回0+残12（7/4/1）を元ID/rule別検証し、Source全体やPTが完了したとは扱わない。期待値は承認SS・明示した標準・手書き032各理由でproduction実行から生成しない。

実行: env PYTHONPATH=tools/quality python3 -B evidence/01_PT/018_NK-OPS-001/input/023_owned_f03_source_context_metadata.py run evidence/01_PT/018_NK-OPS-001/input/032_f03_api_consumer_decisions.json、続いて同post。新PG19930/Pythonmetadataのみ。Product/fixture/JMS/graphhelper/close/rollback/Root/VM/PT/analyzer/既成功再演0。coverage未測定/全F03・451未受入/正式1964-53/技術46/新leaf0/工数null。結果3548/manifestへ日時・環境・HEAD・hash・終了を追跡する。
