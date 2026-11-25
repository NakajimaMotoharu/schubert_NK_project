# 1704 Web media stream取得結線 単体テスト仕様書

NK-OPS-001/P01809/C07/RD171/UI252/SS333351/PG-D564。MediaStreamsMetricCollector constructor/collect/snapshot、新8Test MEDIACONN001..008と必要既Web35を当43/6で普通実行予定。既Protocol MediaType3/既Gaugeのpure範囲だけを呼び、Functionは自己所有fixture、実stream/HTTP/file/VM/Root/DB/配備/native操作0。borrowed supplierとregistryの外側期限/source/asOf/所有真正性・実接続は未受入。

| Test ID | 目的/入力/独立期待値 |
|---|---|
| MEDIACONN001 | constructor source呼出0/3未知Gauge、type毎fixture1/7/19を一読後公開、3key以外増えない |
| MEDIACONN002 | AUDIO未知で同AUDIOだけNaN/empty・VIDEO/MUSIC維持、真0回復、旧OptionalLong7不変 |
| MEDIACONN003 | STANDARDは全type source呼出/保持/登録0、null type collect/snapshot拒否、supplier/registry/mode nullと未知mode拒否 |
| MEDIACONN004 | 既AUDIO7後source Runtime/Errorは同identity再throw、AUDIO未知・VIDEO2不変、例外文面/accessor0・retry0・caller registry closeだけ |
| MEDIACONN005 | source null OptionalLongはNPE非正常伝播、負-1/MINはIAE非正常伝播、同type未知/他type2、MAX原値/double表示、回復fixture0 |
| MEDIACONN006 | 同owner二callerの一方をlatchで停止、後続workerの待機先が先行workerであることを有限確認、第一完了前source呼出増0/旧Gauge不変→各順公開。待機時間だけで成功を推定しない |
| MEDIACONN007 | 64caller fixture入力をproduction呼出前に独立IdentityHashMapへ保存、戻りobject identity/原値と3type別集合・最終fixture100/101/102、別ownerは独立 |
| MEDIACONN008 | constructor第2Gauge Runtime/Error同一伝播/残1/close0/source0、foreign meter衝突も不置換、caller finallyがclose |
| MEDIACONN009 | MUSICの供給元が固定NPEを投げたとき同じ例外を返し、MUSICのみ欠測、VIDEO 5と未観測AUDIOを保持する。回復要求は別のworkerが有限時間内に処理し、MUSICの真の0を公開する。再試行・借用レジストリcloseは0。 |

sourceの単一完全OptionalLongをread→検証→publicationまでprivate lock、STDは詳細source未呼出。snapshotは既atomic観測を読み、provider失敗/null/負値を真0/成功へ変換しない。Runtime/Errorはmissing後元再throwしcause探索/format/retry/closeしない。レジストリscrape間原子性や別ownerへのglobal lockは約束しない。

開始3/5/9pp上限10/fresh API直結eventへ保存、原-v4-v5/旧markerlast27区間null/共有累積null/元90再基底化0。source固定後、7754正常六Main/Test compile（classpath capture指定を明示）→7756当43普通JUnit→7758独立四100/CRC/static→7760全1768/元1669debug→7762全115/99trace→7764生成14/current ordinary/raw全個別理由→7766公開scan、1705結果へ実日時/OS/JDK/tool/command/exit/XML/input-output/CRC/四counter/BUG/hashを結合。期待値はSS literal/fixture入力・独立集合で算出しproduction accessorから作らない。正式1964/53/工数null/QA051final/PTALT0/whole451-native-CHR/actualHOLDを維持。

## 2026-11-24 排他方式の是正

BUG-3741／YKT-2929。対象は私有ロックの入退とMEDIACONN006の待機先確認。供給関数、型別旧Gauge、後続未実行、固定7/11/13、例外後の対象型だけのUnknown、既公開APIは維持する。自PTの二つのworker以外を観測せず、実媒体・HTTPを用いない。PG43808の同一runで四指標・元8期待値・同期指摘を照合する。
