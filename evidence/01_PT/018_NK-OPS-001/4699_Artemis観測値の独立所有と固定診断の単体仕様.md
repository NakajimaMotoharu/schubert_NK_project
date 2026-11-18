# Artemis観測値の独立所有と固定診断の単体仕様

NK-OPS-001、`ArtemisStartupObservation.Evidence`。WBS-P018-10.03/2-照合とWBS-P017-10参照、MQ-001/002/009/010・SYS-004、UI231/251/253、SS321 §13・342 §4・351、PG37452 CATALOG062。全入力は手作成MapとPressure値。製品Coreの既compile成果から五物理を固定し、ブローカー接続を持たないJVMで実行する。比較は値を使い、一般診断は独立期待値 `ArtemisEvidence[observations=<redacted>]` の一行とする。

| Test ID | 入力と操作 | 独立期待 |
|---|---|---|
| PT-P01810-CATALOG-062A | 6成分を作成後、元Mapを置換・消去し、返されたMapに変更を試みる | 保持値は生成時の独立Mapと完全一致。外部からの変更は拒否。一般診断は固定値のみ |
| PT-P01810-CATALOG-062B | 別生成の同値と異なるキー内容で比較して、HashMapから検索 | 同値検索の値が取れ、異値は等しくない。両診断には観測値が現れない |
| PT-P01810-CATALOG-062C | 第2階層の値、深いrole値、pressure値に別々にnullを入れる | 値を所有するconstructorで入力を拒否し、部分結果を返さない |

全3件の正式終了・XML、局所生counterと独立CRC、PMD・Checkstyle・formatを保存する。値の所有に外部処理、並走、再送は非該当。実Artemis、実ログsink、当製品全量451は別条件。
