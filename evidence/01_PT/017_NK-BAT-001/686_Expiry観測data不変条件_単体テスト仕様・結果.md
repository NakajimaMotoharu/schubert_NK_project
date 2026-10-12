# 686 NK-BAT-001 Expiry観測data不変条件（限定PT）

関連DAT009/OPS009/UI251/SS331341343/451、WBS-P017-01.03。MorningDatabaseSession.ExpiryBegins/ExpiryObservationのDB観測data契約subset、実JDBC transaction/所有権は未受入。開始event0513、凍結0.25/0.5/1.5pp、N/T/個別実費null。

| Test ID / method expiry1749末尾 | fixture・独立期待値 | 結果 |
|---|---|---|
| EXP-1749-001 | literal run17490000…/cutoff9/27 15Z、start9/28 02Z/end+3秒、SUCCESS2/2/0/200、SKIP0/0/0/0。freshはend、SKIPはstartとprior audit endを保持、receipt identity/data redaction固定 | PASS |
| EXP-1749-002 | freshの早いend/別Backup target/SKIP結果/audit end-status-target-success-failure-bytes各単独反例、全IllegalArgumentException | PASS |
| EXP-1749-003 | SKIPのend不一致/result非SKIP/audit非prior/exit10、それぞれ拒否 | PASS |
| EXP-1749-004 | begin別step/skip-prior presence両向不一致/null、observation各5null、非microsecond time拒否、I/O無し | PASS |

Expectedは固定literal/count/例外、Productionで生成0。Receiptは既Test-only ExpiryReceiptFixtureが正規gate順で合成bus/kernel値を渡したdataであり実nativeownerを授与しない。失敗PG1749（source4ea627665）の実4成功でもXML header2でactual1、BUG1160/YKT928として未合格のまま保存。新1750 launcher headerを固定method一覧sizeへ統一、外部XML oracleは独立4 IDsで照合する。

最終Testsource4ad683b89787737aaf5fd8804c5ea2b33cfd2a60、Main2741c4546afad6c1e8b6efbd53dfb58144edf7bb変更0。LAN Ubuntu26.04/x86_64/JDK25.0.4/Jupiter5.13.4/Platform1.13.4/JaCoCo0.8.15、dedicated classes/XML/exec、既fixture/JAR/librarybyte前後pin。実行=`PYTHONPATH=tools/quality:tools/quality/vm/050_s1:<fixed pyflakes> python3 -B tools/quality/pg1750_expiry_count_selected.py`、exact4/FES-aborted-notrun0/Werror0/MainCRC0/VM-DB操作0、serverSHA1d8a484744147412f14dd865bd8dfb0758153d735f4978260f7bc0d4741d41c9。

別pg1751_expiry_exact_qualification.pyはunique4/XML/source/fixture/JAR/library/exec/counter read-only資格0、SHA0058b27d98cb0b48a05e7b4a5438017a4292a805caea19ad98075eb9737da63f。旧失敗4を加算0、最終4だけ。残866L/169M/9C/669B（先870/169/9/684から4L/15B減）。fresh全3618未実行、四100/正式1964PT53scope/wholeleaf0/工数率null維持。child03は実owner/reentry/全例外/close及び終了依存未完、NOT_ACCEPTED。

private WorkPG379/pg1749-expiry-observation-selected-v1（不合格）・pg1750-expiry-count-selected-v1・pg1751-expiry-exact-qualified-v1、LAN PG1750-selected-v1/PG1751-selected-qualification-v1。公開686_manifest.jsonへsafe hashes/counterのみ。修正4ad683b89、BUG1160限定工具再試験完了、Production正式品質は未完。
