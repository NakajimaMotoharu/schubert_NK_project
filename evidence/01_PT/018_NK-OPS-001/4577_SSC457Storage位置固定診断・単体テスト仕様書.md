# SSC-457 Storage位置固定診断の単体テスト仕様書

NK-OPS-001、SYS-002/004、UI243/253、SS342/343 §6.2、SS351、PG278、WBS-P003-07、BUG-3227、YKT-2676。ServiceCredentialLocation.read／directory／toString。独立した期待値はSS343の位置契約と固定文。Coreと当runの入力hash、JDK25、XML、静的記録、未到達を公開manifestで照合する。

| Test ID | 合成入力・操作 | 期待値と根拠 |
| --- | --- | --- |
| PT-OPS-CREDLOC-001 | 絶対位置と無関係設定を渡す | 固定位置、固定toString。追加設定を返さない |
| PT-OPS-CREDLOC-002 | 欠落、空、相対、ルートのみ | 全件独立固定診断 |
| PT-OPS-CREDLOC-003 | 別caseキー、親成分、NUL、CR、LF | 全件独立固定診断 |
| PT-OPS-CREDLOC-004 | 上限4096／超過、nullキー・値・map | 許容境界と独立診断。map自体のnull契約は元試験どおり |
| PT-OPS-CREDLOC-005 | 同一固定値と専用workerの32件 | 全員が指定同値、worker 終了を有限時間で確認 |
| PT-OPS-CREDLOC-006 | 実ファイルを参照せず合成した、OSの字句変換で受理できないJava文字列 | 厳密なIllegalArgumentException、固定文、causeなし、suppressed 0件。実入力を持つ原因を維持しないSS343 |

通常PTは閉じたhost profileで元全5件と新規1件。再送は当値変換に適用されない。実サービス、実ディレクトリ、実credential、本人性確認は本仕様の観測範囲外。実行環境・コマンド・結果・coverageは結果書および公開manifestへ記録する。
