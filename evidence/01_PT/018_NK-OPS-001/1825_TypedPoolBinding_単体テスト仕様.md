# Typed borrowed pool binding→refresh/context/HTTP 単体テスト仕様

NK-OPS-001/RD171 MON010～013/UI252/SS311342351/PG-D621、group2055/主P018-09・C07追加費0。開始fresh45残55/reset1793382075・見積3-6-10pp/cap10。新ApiDbPoolMetricBinding/WebDbPoolMetricBindingは借用HikariPoolMXBean/ConfigMXBeanと一つの既collectorを強保持し、refreshはcollect、snapshotはlast immutable metadataだけ。pool/config/Connection/JMX lookup/control/credential取得・closeはしない。SDKは既contextが所有、bind constructorはnull/mode検査とmetadata登録だけでsource getter未読。

新APIPOOLB001～010/WEBPOOLB001～010各10＋既HTTP Unit新APIMHTTP020/WEBMHTTP020=新22。変更HTTP Unitの必要旧各19=38、actual60/4予定。独立Fixtureは既DbPoolMetricObservationTest.Fixture/WebDbPoolMetricObservationTest.Fixtureのpublic interface proxy（private reflectionなし）。その二outer @Test群はhelperとしてcompileするだけで実行選択/新規合格にしない。actual Hikari/DB/defaultserver/VM/Root/manager操作なし。

|新ID（各role）|入力/操作|独立期待|
|---|---|---|
|POOLB001|null pool/config/registry/mode、未知mode|入力境界拒否・getter0/series0|
|POOLB002|DEBUG ctor→refresh、API3/5/2/8・Web1/1/0/2|ctor未読/初期unknown NaN、四read順序一回・numeric固定値/series4|
|POOLB003|既知→max0→真0/正max|unknownへclear/NaN、真0は既知、series増加0|
|POOLB004|STANDARD、読むとErrorになるgetter|getter0/series0/空snapshot|
|POOLB005|四getter各Runtime failure|元identity/後続readとretry0/全値unknown、明示refreshで回復|
|POOLB006|直接Error|元Error/空snapshot・NaN、normal化0|
|POOLB007|fixture変異・snapshot借用|last snapshotは不変、次refreshだけ更新・鮮度証明ではない|
|POOLB008|実部品context Consumer接続、二render|承認family四値が固定literalで変化、SDKはcontextだけclose/借用bean controls0|
|POOLB009|四getter Integer.MAX_VALUE|long/doubleへ正確、clamp/wrap/0補完0|
|POOLB010|own二worker・first getter latch/second BLOCKED|同一retained collectorがserialize、四read×二回/series4。親は解放後にFuture/getter確認、30秒上限・sleepなし|
|MHTTP020|新binding→context refresh→既Handler二memory GET|200/ready1/approved値・UTF8 byte長/header/close1、max0後はNaN/empty snapshot（0へ偽装0）|

期待はSS承認name/tag、API/Web固定数値・four read順序、NaN/真0の区別、元例外identity/owner、明示HTTP header/status/byte長の独立算出。production refresh/renderでexpectedを生成しない。snapshot/daemon/source不変をactual runtime生存・全scrape atomic/freshness/healthと誤認しない。

8832正常six PT0→8834 actual60/4→8835既collector六raw PMD rationaleのsource/rules不変・当XML資格への結合（旧PT/coverage転用なし）→8836当Binding2/collector2/HTTP2の全line-method-class-branch100/CRC/session/static→8838全1834/旧1832不変・原1667/owner227/五edge/typed read-only所有と旧HTTP19本文保持→1826/scan/push。新二Binding straight-throughでも基礎collectorを当source実行してbranchを測定し、branch0を仮100や除外で隠さない。collector既三警告ずつのprivate lockとsame-primary missing契約は7372/8132のsource固定個別理由を参照するが、当rawを消さず新60/実四counterとjoinする。未分類・新指摘は合格にしない。

全command/UTC/OS/JDK/tool/branch/commit/input-deps-Jar/tool/exit/XML/coverage/BUG/hashはmanifest/resultへ。着手時60 UNRUN、元4222/104確認再演0、既成功転用0/除外・抑制0。Root callerでのactual Hikari bean供給/owner assembly、manager raw40/必要契約19当XMLjoin、実native/CHR/whole451/正式1964-53/原190新受入0・工数null/QA051final/PTALT0/全actualHOLD・原本等/元-v4-v5維持、小区切り全体停止なし。
