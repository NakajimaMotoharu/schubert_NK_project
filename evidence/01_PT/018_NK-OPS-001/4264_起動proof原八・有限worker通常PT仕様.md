# StartupProofFrame 原8件・有限worker通常PT仕様

NK-OPS-001、WBS-P018-03 / 費用WBS-F03追加資格 .3/.9/1.8pp上限3。SYS002/004・OPS009、UI212/251、SS341/342/343。BUG2865/YKT2387を修正前PG30066へ登録済み。Main変更なし、public値のparser/encoder/不変性だけ。

| Test ID | 元method / 独立期待値 |
|---|---|
| PT-OPS-PROOF-001 | proof001: Test手書きNKSTART1/17行ASCII・順序golden、個別値/固定redaction/proof_fd不含 |
| 002 | proof002: 17keyの欠落/未知/重複/順序/版/終端LF破損を拒否 |
| 003 | proof003: 非ASCII/制御byte・0/8192/8193・null引数/key/value/未知名。cloneによるborrowedinput不変 |
| 004 | proof004: literal pid/start/fd/u64/uidgid上下境界・overflow/非正準decimalを拒否 |
| 005 | proof005: 昇順unique群1..16、空/重複/逆順/0/overflow/17群を拒否 |
| 006 | proof006: API/WEB・非zero正準UUID/32hex・64lowerhex、固定hash比較 |
| 007 | proof007: 元Map消去/返却Map書換拒否/入力output消去後のsnapshot不変 |
| 008 | proof008: 独立32task/8workerで同手書きgoldenのparse→encode各byteをassert。Future各5秒、finally shutdownNow/await10秒・未終端fail |

元8のgolden/全期待値を保持。workerを有期限化するため実sourceを変更し、この変更後のwhole8だけを新しい単一runで実行。期待値をproduction methodから作らず、Testの固定textblock/境界literalを使用する。架空の権限を発行するものではなく、既存public Testに元からある非秘密値のbyte文法だけ。実Root/permit/FD/native/DB/VM/鍵/Backup/Unit/intent操作0、HOLD試験の抽出0。

全Main1+Bounds/Field計3physical、全Test1/元8定義をGJF→RootNullAway/lintWerror→PMD/Checkstyle/SpotBugs→適用性原票→preflight→Git source固定→一whole8→独立post。XML/FES/CRC/初期化/単一exec/全source四counterを照合。未達はそのまま保存し、manual除外・反射到達・無意味assert・旧exec合算なし。実JVM Code methodと既定JaCoCo generated filter差も別記。実行command/source/OS/JDK/tool/終了・input/output/hashは各manifest、結果文書に固定。全451/元190受入/実起動/生成code除外承認への転用なし。
