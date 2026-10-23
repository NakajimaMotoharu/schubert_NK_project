# 1600 監視Poll・Heap結線 実行結果

source `0b8aa6dab9b91d378811b0bda24d6a61bbc73106`、1599/PG-D533/group1848。PG7210-heap-connection-host-v1原SHA `7a573b70b7e8d23754f152b8d9635173008e60186eff2537c05beecef950397e` は真正verify0/124PT17suite/FES・rerun/flaky0/六format0。新16と既108の当source必要回帰を分離し、旧source108成功を合算していない。

PG7212-heap-connection-post-v1原SHA `f42c119d34dbe54c5c22f8f75f0d1b1eab80f20b648c419c4ba9d6138e50aa58`：全36Java source/実28class＋metadata1・単一session/CRC0、**L516/M121/C28/B237全miss0**。親Enforcer/lint/Werror/NullAway/六format、SpotBugs/Checkstyle0、PMD raw23/exit4/processing0。PMDの同数は無変更を意味しない：FilesystemHealthMonitorの旧private同期二＋同一例外伝播四を除去し、MonitoringPollerへprivate同期二＋同一例外伝播四を移した。旧残17行は対象Mainが同byte。共通pollはprivate final lockで入力→同owner評価→commitを一方向に直列化し、Runtime/Errorを正常化・retry・文字列化せず、次観測の連続性だけ切断して同一例外を再throwする。lockの外部公開/抑制0。全行の機械照合は1602へ分離。

POLL001～008はexact callback結果/回数、失敗identity、逆行の事前拒否、clock失敗後の新旧API gap、全null境界、null callback結果の未commit、非atomic counter64並行の一意1..64、回復時のgap一回消費を独立assert。HEAPCONN001～008はheap getter・clock・kernelの実接続、75%600秒直前/丁度、max未知と故障の回復切断、clock失敗でgetter未実行、明示OOM報告とusage未知の分離、null/逆行で副作用0、二owner分離、64並行count65/旧snapshot不変を確認。fixture内の合成OOMは実メモリ枯渇を起こしていない。

実JVM/GC/JMX接続/FS採取/Root/期限/owned停止/実OOM制御/標準exporter/HTTP/native/CHR/全scope同source451は未受入HOLD。新障害/上位変更0、正式1964/53・歴史17/別source新7/原190新受入0/工数null/QA051final/PTALT0不変更。原本DBBackup/鍵/stash/native/Currentbaseline不変。開始終了・OS/JDK/tool・branch/source・command/終了/XML/coverage/static/hashは原7210/7212へ一意結合する。
