# 親単調30分budget PT仕様（PG366、実装前）

Program NK-OPS-001、予定class/method `MorningParentBudget.create/requireWithin`、`MorningBackupUnitCycle.execute`の同budget受領。RD OPS-009/BAK-001、UI251、SS341§5-6/342/343、SSC107、BUG322/YKT254。時計はsystem wall clockではなく単調nanoTime、30分固定。Production外部Morning entry開始時に一度生成して各親stepへ借用する設計とし、Backup内部factoryで新しい30分を発行しない。

| Test ID | 入力・操作 | 独立期待 |
|---|---|---|
| PT-OPS-MBUDGET001 | 起点0、29分59秒999999999ns、30分ちょうど、30分超を固定LongSupplierで再現 | 直前だけ通り、境界以上は固定IOException。期待nano秒数は30×60×10^9を試験側で定数化 |
| PT-OPS-MBUDGET002 | nanoTimeの符号wrap（MAX-10から15ns）、逆行、同値、複数stepで同じinstance | wrap直後15nsを通し、逆行を拒否。異なるstepで期限を再起算しない |
| PT-OPS-BUCYCLE006 | pre-start期限切れ、start後receipt待ち/stop待ち/retire直前の期限切れ | pre-startはstart0で拒否。post-startはstop/retireへ進まず保持port1、marker保全。SS341の親全体budget oracle |

null supplier/budgetは構築で拒否し、NPEを正常値へ変えない。合成portは公開fixture、expectedをProduction methodで生成しない。実Unitの`TimeoutStartSec=30min`、SIGTERM/SendSIGKILL=no、M/A/marker/currentと次回admissionは隔離VM実測で別に確認する。選択/全6command・commit・coverage・RED/GREEN結果・hashは245へ記録する。実Backup archive/Cleanup/permit/外部Web/API/CHRの代用にしない。
