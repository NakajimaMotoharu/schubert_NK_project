# 2524 StartupProofFrame 現whole8通常PT仕様

2026-10-29、PG-D827予定、source0061d178c/normal13832 SHA8a3edc7a…/全1843静的13838 SHA7625ceb8…。開始0.5/2/4cap10、主F03/既canonical担当費参照P01803・追加0（13846 sourceRowsで開始前照合）、event2906にfresh値を保存。旧予算/全995runtime/正式/QA051final/全actualHOLD不変更。

## 対象とPT_DEFAULT

NK-OPS-001/SYS002004/OPS009/UI212251/SS341342343/SSC086087/PG295。StartupProofFrameTest全276行/八methodとMain全137行を読取。Test SHA658c1736b4d4d0927d4db12eac869c5bf66dd8a29c862993d26780d52341fa59、Main SHA54f06205d273eb7bc60edaec6a1e532f206b73c13565c23a9dd04807a32848e7。既13400の一private文字列定数化後の当whole未資格、2047のselector source理由は動的PTの資格ではない。

18行の手書NKSTART1公開placeholder ASCII（1/2/3連続UUID/Invocation・a/b/c/dのSHA文字列、admission_fd=128はただの文字列）とMap/byte/BigIntegerのencode/parse検証だけ。実FDを開かず、署名/permit発行・権限確認・実Root/owner/VM/DB/credential/鍵/nativeを呼ばない。MainはJDK値操作/固定schemaのみ、factory/native依存0。自己pool8/32taskは外host180秒制限内、submitを実processへ接続しない。wholeの一部抽出/既拒否検証の別caller再試行0。

|Test ID / method|入力・操作・独立期待|
|---|---|
|PT-OPS-PROOF-001|全17fieldの手書goldenからparse/Mapからbuild、encode期待は同goldenの固定byte。field順/予約proof_fd不存在・redacted表示を明示比較。Production encoderからexpected生成0。|
|002|全fieldの欠落/extra/重複/順序/未知名/header/末尾LFの差分を一つずつ作り固定IllegalArgumentException/message・cause/suppressed0を要求。|
|003|ASCII byte0/9/13/31/127/128/255、長さ0/8192/8193、API/Map key/value/field名null、元入力byte保持を独立比較。|
|004|pid/start/admissionFd/device/inode/uid/gidのSS下上限と外側・符号/leading0/空白/overflowの手書数値を比較。|
|005|group1～4294967294/最大16個・昇順/重複/逆順/空/未知/17個境界。|
|006|API/WEBだけ、boot/epoch/Invocation UUID下位文字・非nil、固定64 lowercase SHA domains。大文字/長さ/未知値を拒否しa/b/c/dの固定期待へ比較。|
|007|入力Map/byte消去・出力byte消去後もsnapshot不変、fields変更拒否。|
|008|独立32taskが同goldenを処理し全byte一致。並行性の期待は固定goldenで、別Production関数をoracleにしない。|

各vector/loopは八JUnitの内数、null契約・異常・例外・並行を含む。再送・実認証/権限・kernel ownershipは本データ型の適用外/別HOLDで未認定。新Test ID/source変更0。

command=`python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg13854_startup_proof_whole_eight_pt.py`。JDK25.0.4/JUnit1.13.4/JaCoCo0.8.15、空ENV/config・固定六jar/SDK、共有reporterの単一Map count8。13856で元XML/FES-abort-container0・全源/Jar・一exec/session/CRC・Mainと全nested Bounds/Field（三physical）の完全source unit counterを独立測定、missは保持。既定filter不変更・除外/reflection/旧exec union/旧source転用0、全PGPT/451/実Rootの資格とは分離する。実時刻/command/exit/hash/coverage・関連BUGは2525と専用manifestに記録し、その後も独立PG/PTを継続する。
