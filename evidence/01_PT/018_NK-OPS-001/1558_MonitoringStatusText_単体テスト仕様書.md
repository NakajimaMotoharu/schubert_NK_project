# 1558 MonitoringStatusText 単体テスト仕様書

2026-10-23、NK-OPS-001/P018-09/C07共有参照、PG-D522。SS351§7のlocal status/管理者確認を、既pure監視経路の閉型出力として補完する。着手見積0.5/1.5/3pp・上限10pp、共有8/残92/reset1793306748/元開始0。scope/モデル/451条件を変更しない。

対象は非I/OのMonitoringStatusText.render(mode,List<Event>)。固定scope marker付きtextを返すだけでstdout/journal/fileへ書かない。これはSS351 structured log event、HTTP health/readiness、実監視/原因撤去/owner/Unit/permitの証拠ではない。新log action/error/metricを追加せず、JSON log encoderの代用品にしない。Caller supplied snapshotの表示専用であり、frameを起動/停止判断へ流用しない。

Frame: `# SUPPLIED_MONITORING_STATE_V1 MODE=<STANDARD|DEBUG>\n`、次に固定column `condition\tservice\tseverity\tcount\tfirstSeen\tlastSeen\n`、open event一件一行。ConditionのSS351順/Serviceの閉enum順、countはdecimal/時刻はUTC ISO8601 millisecond（sub-ms切捨て）。STANDARDでもbasic alert表示は残す。自由text/ID/path/例外/credentialを受け付けるAPIを持たない。closed又は重複key入力は固定IllegalArgumentException、null list/element/modeはnon-null契約違反として拒否し、状態を変更しない。

PT_DEFAULT：純粋値/format/自己所有executorだけ。新6PT＋既48の必要同package回帰=54、実行15class＋metadata1、四counter100/CRC/単一session/static・実Jar byte接続を要求する。Production POM/依存は不変更。実サービス/実log送信/Root/VM/DB/鍵/配備は行わない。

|Test ID / method|独立期待値・観点|
|---|---|
|PT-OPS-MONSTATUS-001 / monStatus001|空STANDARD/DEBUGは固定二header行だけ、両modeでbasic status表示。ready/authorityを示すfieldなし |
|002 / monStatus002|単一WARNINGのliteral frame、count1/固定key/UTC .123ms、sub-ms切捨て、caller list変更で既String不変 |
|003 / monStatus003|逆順三event（同condition異service含む）を固定順へ。count/最終違反時刻/CRITICALを失わず、元list順不変 |
|004 / monStatus004|null mode/list/要素・同key重複・closed snapshot拒否、固定診断/owner state不変 |
|005 / monStatus005|Instant.MIN/MAXのISO extended year millisecond、0ns/999999999ns境界の独立literal。壁時計を判定clockとして使わない |
|006 / monStatus006|64並行callerで同literal frame、共有Formatterは不変、executor finally終端。任意log/user値を受け付けるAPIなし |

Expectedは上記frame literalとSS351閉enum/固定時刻/decimalから手書きしProduction renderから生成しない。DateTimeFormatterはJDK25の標準変換だけ、Locale.ROOT/UTCを固定する。状態/観測の再認証や実Source世代の推測なし。実command/source/OS/JDK/tool/hash/actual exit/XML/counter/static・未実行は1559以降のnewonlymanifestへ保存。sourceの異なる48/5/4/旧4222を一つの合成全体合格へ加算しない。
