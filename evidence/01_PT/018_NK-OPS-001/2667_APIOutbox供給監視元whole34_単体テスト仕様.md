# API Outbox供給監視 元whole34：単体テスト仕様

2026-10-30 / PG-D898 / WBS-F03・P01809 / source6b53efeec87f3ec36a840dd8e7759656cb4aee5c / branch dev-foundation。着手event3057、群見積0.5/3/6pp・cap10。元Collector8/Repository10/Rows8/Ages8=34/4、全1304Test＋四Main295行のbody/helper/initializerを確認。関連RD171・UI252・SS332/351、既1647/1660/1664/1668、OUTBOXCONN001..008/DB001..010/MET001..008/AGE001..008。Test IDは元classname#methodとXMLで一意join。

## PT_DEFAULT・期待値

自己所有のJDK Connection/PreparedStatement/ResultSet Proxy・SimpleMeterRegistry・2/8有限thread64taskのみ。実DB/driver/network/VM/Root/配備/鍵/cohort/graph分類器0。原Main/Test/Fixtureを改変・抽出せず、拒否対象の代替実行ではない。

独立literalSQL `SELECT status, COUNT(*) AS row_count, MIN(created_at) AS oldest_created_at FROM schubert.mq_outbox GROUP BY status`、READ_COMMITTED/readOnly/autocommitfalse・timeout1・query一回・RS→PSclose後公開。借用Connection変更/close禁止をProxyの未知method拒否で検査。固定count3/5/7・age2/4/11秒、空/疎0、JST→UTC1.5秒、0001→9999の315537897599秒999999000ns、LongMAXとDurationMAX、1ns→0.000000001・double0x1.0p63、null/欠落/未知/重複/非正/未来・SQLnullを元expectedにする。期待値をProductionで生成しない。

六series API/status固定・STANDARD収集0・NaNと既知0分離・失敗で両familyとlastObservation無効・再成功回復・借用registry保持・partial factory identity、例外同一物/抑制RS-PS順序/prepare-execute回数、有限latch前後公開とowner並行64task。record Ages hash3045/Snapshot96447と固定全文は独立JDK record多項式・既知値。Countsの生成contractは依存Snapshotからのcoverageも含む実測値を記録し、無assertionの人工試験を増やさない。

## command・証拠

PG14421は固定hash/必須text/直接接続API禁止と反例だけの非実行補助チェック（権限overrideでない）。その証拠を固定後 `python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg14422_api_outbox_supplied_whole_thirty_four_pt.py`。normal14216/六Jar/元全currentinputsと原SDK・自己検証済みReporterを使い、一JVM/session/exec。PG14424は元XML/真exit/一CRC/元環境と全四Source八physical（Collector1、Rows3、Ages2、Repository2）の実fourcounterを独立照合。自然branch0/未達をそのまま保存し、手動除外/exec合成/旧source成功流用0。

結果2668・path/hashは公開manifestへ。元312/成功回帰の確認再演0。正式1964PT/53scope・歴史17/190・別source register・工数null・QA051final・全F03/451・既HOLD/原本保全不変更。
