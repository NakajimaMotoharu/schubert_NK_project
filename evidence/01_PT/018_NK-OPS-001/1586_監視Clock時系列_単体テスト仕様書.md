# 1586 監視Clock時系列 単体テスト仕様書

NK-OPS-001/P01809/C07・RD171/UI252/SS351・PG-D530、対象MonitoringObservationClock constructor/contextとFilesystemHealthMonitor.observeNow/observeLocked・既明示context経路。借用Clock.instantとLongSupplier ticksだけを使い、実Root/OS時刻変更/VM/ネットワーク/DB/鍵/配備操作0。constructorで一epochのtick原点を固定、符号付き原点とLong.MAX→MINの通常wrapを許可し、差分は同epoch<2^63ns（約292年）というnanoTimeの契約で扱う。逆行/長過ぎるepochは固定診断で拒否し、現在時刻やbaselineを自動再設定しない。

| Test ID | 目的・fixture入力 | 独立期待値 |
|---|---|---|
| OBSCLOCK001 | 原点100、ticks100/102/2100、固定UTC/UTC rollback | elapsed0/2ns/2000ns、実UTCを捏造せずそのまま、CauseClearance保持。 |
| OBSCLOCK002 | 原点負、Long.MAX−3→Long.MIN＋1 | 5ns、signed origin拒否/誤った負elapsed0化なし。 |
| OBSCLOCK003 | 原点0、Long.MAX、次Long.MIN | 9,223,372,036秒854,775,807nsまで受入、次epoch超過拒否・状態不変。 |
| OBSCLOCK004 | 一度5へ進んで4へ逆行→6 | 逆行IAE/UTC未読、次6nsで原点変更/自動reset0。 |
| OBSCLOCK005 | Clockのnull/Runtime/Error/非formatable、tick例外/constructor例外 | 同一例外伝播/NPE境界拒否、未返却contextはlast未更新、例外原文処理0。 |
| OBSCLOCK006 | constructor null・cause null/再利用 | 明示拒否、cause nullはtick/UTC読取0、既context immutable。 |
| OBSCLOCK007 | 64並行・atomic tick1..64/固定UTC | 全duration集合1..64ns一意、clock/tick各呼出回数、外部source close/zone変換0。 |
| OBSCLOCK008 | health input＋clock、UTC rollback/Clock欠測/unchecked FileStore故障・legacy経路 | warning/criticalの経過はmonotonic、Clock/入力失敗が次正常期間の連続性を切断、既eventを偽close0。失敗は再throw、null時provider0/異常context逆行は既状態不変。 |

新8件と同package必要回帰83を同sourceで通常実行する。Expectedは固定UTC/明示ns/Long boundaryの独立秒・nano値/固定Severity・countから作り、production methodでexpectedを生成しない。Clock失敗をPT PASSへ正規化せず期待する拒否をassertし、skipped/not-run/flakyを除く。新clockとhealthのprivate lock順はHealth→Clock（時刻採取後解放）→TimedMonitorで逆向きcallなし。実provider有限性/epoch所有・polling間隔/制御・owner停止/native/全体451は未受入。実行command/OS/JDK/commit/終了/XML・四counter/静的適用性・実Jar/trace/BUG/hashは結果へ記録する。
