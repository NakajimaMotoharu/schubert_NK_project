# F02 application/domainとStorageの依存境界

SS311 §3 SSC-021、WBS-F02-b、BUG-3367・YKT-2718。API/Web moduleの通常の依存可能範囲内でも、application/domainは低位Storageへ直接依存しない。Java25／ArchUnit 1.4.2、六合成JARの型情報のみを読み取る。moduleの実appや保留型は起動・読取しない。

| Test ID | 合成条件 | 独立期待 |
| --- | --- | --- |
| PT-F02-APPSTORAGE-001〜004 | API application／domainとWeb application／domainから直接Storageの型を所有。domainは配列も含む | 四指摘 |
| PT-F02-APPSTORAGE-005〜007 | API/Webのfile adapterとBatch fileがStorage型を所有 | 指摘なし |
| PT-F02-APPSTORAGE-008・009 | API/Webのapplicationが自moduleのfile adapterへ依存 | 指摘なし |

PG40432は5/9、禁止4未検出。修正後PG40434は9/9。既禁止合成によるArchUnit終了1は意図した診断。PG40436で16同一合成classfile、禁止4だけの追加、許容5の維持を独立確認する。現在の明示package source照合は現実JARの代用にしない。製品PT、実六JAR、全451、正式は別範囲。

[独立照合](evidence/PG40436-f02-application-domain-storage-independent-v1/manifest.json)
