# NK-OPS-001 Publication限定復旧・strictGC独立照合仕様

Program/class: MorningPermitPublication、BackupStartIntentFiles、RootStartupContext、publication-only recovery工具。RD OPS009/SYS-004、UI251、SS343/353（SSC266/268）。Production source769ddb15cd735c25fef581b5f9850ef9d0053c0f、VM PG1292、dev-foundation。WBS活動leaf P018-03.03（主担当P018-03）、原本継続P017-02/Backup intent P017-06は参照依存であり費用を重複加算しない。

PT-OPS-PUB-RECOVER-003: PG1505の凍結115member/署名/helper ABIを確認し、別PG1506 stage、PG1507 fresh M→A・同peer readonly DB/advisory・十Ref・全原値認証を行う。真正PID1/vendorによるExpiry→Artemis→Cleanup逆順一回停止、全本人/task/FD/lock消失、canonical型付きintent退役とdirsync、全scope正常終了を期待する。既INVALID/permit・原本・DB・Backup・credential・nativeは不変。旧Root1456の143を成功へ変換しない。

PT-OPS-PUB-GC-001: PG1510純粋bridgeの独立2試験。手書きwarm/current fixtureで18属性各変異・全32設定・未知/非zero/null・異Root/片側変更を拒否する。GCが許されるのは停止済三Unitの厳密closed schemaのみ。ExecStart宣言path/argv/ignoreerrorsを維持し補助履歴の閉鎖schemaを照合する。独立期待値から全fieldを指定し、Production呼出しでexpectedを生成しない。

PT-OPS-PUB-GC-002: PG1511 separate fresh readonly二読。保存warm停止receipt/真正PID1/vendor/hashを保持し、current strictGCと分離して全原値・資源消失・新Ref正常返却を照合する。GCゼロだけでは停止証拠又は次の起動権限を認定しない。PG1508拒否1/BUG1120は原証跡のまま保持する。

実行command: `python3 -B tools/quality/pg1505_publication_recovery_compile_v3.py`、同1506 stage/1507 once/1511 closing。これらのmutation commandは実行済みで再実行禁止。独立試験だけは `python3 -B tools/quality/pg1510_publication_gc_bridge_test.py`。JDK25.0.4/Ubuntu26.04.1、詳細source/hash/終了codeは662及び公開manifest。Production coverage増分0、要求四100は未達のまま。関連BUG1115/1120、YKT883/888、SSC266/268。真正親DONE、別fresh一回resume、native/正式品質は別未完。
