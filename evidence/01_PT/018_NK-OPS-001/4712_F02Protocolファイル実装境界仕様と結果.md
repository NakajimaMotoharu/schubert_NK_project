# F02 Protocolのファイル実装境界

SS311 §3、WBS-F02-b、BUG-3364／YKT-2717。Protocolのcodecからファイルの実装を直接呼ぶ例と、同じJava APIが別責務に属する例を合成classfileで確認する。Java25／ArchUnit 1.4.2固定。class初期化、ファイル操作、サービス、API/Web製品JARは範囲外。

| Test ID | 入力 | 独立期待値 |
| --- | --- | --- |
| PT-F02-PROFILE-001〜004 | ProtocolからFiles、FileInputStream、FileChannel、FileSystemProviderの各操作を直接呼ぶ | 各1件のフレームワーク境界違反 |
| PT-F02-PROFILE-005・006 | ProtocolがPathを値として表示し、借用InputStreamを読む | 指摘なし |
| PT-F02-PROFILE-007・008 | StorageとBatchのfile adapterがFilesを呼ぶ | 指摘なし |

初回PG40414は4/8、禁止4が未検出。修正後PG40416は8/8、禁止4だけを検出。意図的な禁止例を含むため修正後の解析器そのものは終了1。PG40418で同一14合成物理と、実Protocol JARの現176物理を保存済み型付き2,609辺に照合し、対象型の辺0を確認。新しいJAR build／jdeps／製品PTは各0。全六JAR・全451・正式受入は別。

[独立照合](evidence/PG40418-f02-protocol-file-independent-v1/manifest.json)
