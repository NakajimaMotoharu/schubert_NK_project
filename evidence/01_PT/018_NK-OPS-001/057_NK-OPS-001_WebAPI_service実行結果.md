# NK-OPS-001 Web/API service unit実行結果

2026-09-25 PG269選択段階: JDK25.0.4/Maven3.9.12、`ApplicationServiceUnitTest`のPT-OPS-SVC-001～004を4/4、failure/error/skipped0で確認。`systemd-analyze verify`はtest-only `/bin/true`を一時renderした構文試験であり、実Web/API process、credential配布、DB/JMS接続、readiness、管理port、実NK CHR-A01/L01を起動・認定していない。最初の選択Maven commandはreactor依存moduleに対象testがなくexit1、次の選択commandはSpotless未適用でexit1。いずれも合格に算入せず、format適用後のAPI選択4/4のみ暫定GREEN。正式全reactor/coverage/SpotBugs/53scope/hash待ち。関連障害なし、QA-045回答済み。秘密実値は保存しない。
