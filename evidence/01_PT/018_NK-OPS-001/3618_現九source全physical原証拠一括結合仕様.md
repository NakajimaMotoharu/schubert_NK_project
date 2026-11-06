# 現9 source・全physical原証拠一括結合仕様

G13.07、開始.5/1.5/4pp・cap6。21866の9つの証拠結合残行だけを対象とする。Comparator/TargetAdapter/Guard/LogAudit/Outbox/LogCleanup/Acceptor/Menu/Traceの元実行を再演しない。Root/VM/native/backend/held fixture・Product実行なし。

PT-OPS-SOURCEJOIN001（metadata）：current normal20990とtool21088の固定JARから、classfileのSourceFile属性を読み、各package/Java sourceに属する全physical（nested/synthetic/interfaceを含む）を確定する。Test名やclass名prefixだけで分母を推測しない。対象package内のメモリ読取だけで、classをdiskへ抽出しない。元証跡の各physical SHAと全件一致、元source commitのMain byteとcurrent disk・normal入力hashが一致することを要求する。

PT-OPS-SOURCEJOIN002：元原XMLのsourcefile counterを直接照合し、line/method/class未達0・存在するbranch未達0を確認する。自然branch0やno-code metadataはN/Aのまま。compiler既定filterの空class nodeを削除/合成しない。元F/E/S/aborted/終了0と原case集合・独立仕様参照を保持する。対象fileの全physical/counterが揃っても、現在の全依存の実行資格・個別WBS/全451/Runtimeを自動受入しない。

不足/byte差/全source未達は該当rowをpendingとして具体的差を保存する。再実行やoracle変更で補完しない。参照したケース数は重複する元runごとに一回とし、sourceごとのTest数を足して新実行件数にしない。工数率null・新method/source証明/leaf受入0、正式1964/53・全HOLDを維持する。
