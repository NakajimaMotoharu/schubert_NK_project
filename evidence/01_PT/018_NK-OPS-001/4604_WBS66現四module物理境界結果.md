# WBS66 F02 現四モジュールの物理境界

Core d0b8ee6057132d73f0234becf9fdef3073308f87、PG38766。PG38764で資格確認したProtocol176、Storage79、Bootstrap201、Batch646の合計1,102物理を再ビルドせず使用。ArchUnit 1.4.2は実49,830参照と36,719 code unit accessを解析。製品を解析プロセスのclasspathへ入れず、JVM初期化0、前後で全class SHA一致。

Batch→Bootstrap715、Batch→Storage1,664、Bootstrap→Storage324のみ。禁止artifact辺0。既知のStorageIoException→java.sql.SQLExceptionは1件で真正終了1、BUG3233／YKT2680を維持。API/Webの実class、Artemis、全targetのF02・451は未成立。元設定の抑制や除外なし。

証跡 evidence/01_PT/018_NK-OPS-001/evidence/PG38766-f02-current-four-physical-architecture-v1/manifest.json SHA256 27befbd724e2725dbac2fced8af3a956af8cfdfbef3742c205b58563214683e0。
