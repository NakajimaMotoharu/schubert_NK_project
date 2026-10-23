# 1591 JVMHeap健康入力 単体テスト仕様書

NK-OPS-001/P01809/C07、RD171/UI252/SS351§7、PG-D531。対象JvmHeapHealthObservation.from/private constructor/read、HealthUsageRatio.fromUsed、FilesystemHealthObservationの同算出処理の抽出。外側が検証したMemoryMXBeanからheap-readだけのSupplierを借用し、binding時operation0、poll一回でgetHeapMemoryUsage一回。ManagementFactory/実JVM操作/GC/verbose/dump/JMX接続/VM/Root/DB/鍵/配備0。標準JVM metricは製品/Micrometerのままで独自metric/backendを作らない。

使用率はused/max、max=-1または0はUNKNOWN、committedへの分母変更をしない。比率計算はFilesystemの既独立byte/IEEE oracleを保持して同package純粋converterへ抽出、75/80/90/95等の整数thresholdをdouble丸めで一byte早く跨がない。unchecked/provider NPE/Errorは同一伝播、catchして正常値へ変換しない。bean/統計の実owner同定・時系列/alert接続・OOM時の実プロセス停止は別の未受入条件。

| Test ID | 入力・操作/目的 | 独立期待値 |
|---|---|---|
| HEAPINPUT001 | getter-only自己所有bean、binding後0/read一回、used0/750/900/1000 max1000 | 0/75/90/100、heap getterだけ各一回。他bean operation/identity/GCアクセス0。 |
| HEAPINPUT002 | max=-1/0、committed100/0、復旧後max1000 | UNKNOWN、committedを分母/0%へ変更0、次75。 |
| HEAPINPUT003 | Ratio直接負used/used>max/非正max/正常 | 範囲外UNKNOWN・clamp0/100捏造0、正常25。固定整数表。 |
| HEAPINPUT004 | total10^18、75/90の一byte直前・丁度・直後 | 明示IEEE直下bit、境界未満/以上を保持。 |
| HEAPINPUT005 | Long.MAX/単一byte/最大空満 | 0/100、long乗算overflow0。 |
| HEAPINPUT006 | bean null/統計null、未知失敗後の再使用 | 境界NPE・借用bean operation0/一回、未観測正常化0。 |
| HEAPINPUT007 | 非formatable Runtime/NPE/Error/合成OOMのgetter故障 | 元例外同一・再試行/format/GC/dump0。実memory枯渇を起こさない。 |
| HEAPINPUT008 | 独立二bean binding/64並行read/固定MemoryUsage | getter64・全75と別source50を分離、各sourceの所有/観測に副作用0。 |
| HEAPINPUT009 | getHeapとgetNonHeap等の罠/immutable旧snapshot/別used | heapだけを選ぶ、元MemoryUsage/新旧ratio snapshot値が変異しない。 |

FixtureはMemoryMXBean interfaceの自己所有proxyと固定MemoryUsageだけ。期待値は固定byte/最大値/IEEE bit表から作り、production methodによるexpected生成0。既Filesystem FSINPUT001..010/clock8を同sourceで回帰し、旧oracle変更0。新9を含む監視100件・14suiteと当全production class/line/method/branch100/単一sessionCRC/静的全指摘・正常六Jar/traceを結合する。実行環境/source/command/終了/XML/hash/BUG/残リスクは結果へ記録し、全体451/正式/PTALTへ加算しない。
