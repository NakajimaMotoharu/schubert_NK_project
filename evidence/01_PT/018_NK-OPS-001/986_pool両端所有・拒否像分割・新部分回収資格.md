# pool両端所有・拒否像分割・新部分回収資格

2026-10-16、NK-OPS-001、SS342/343/353・SSC293・QA047・BUG1349～1352/YKT1115～1118。Production7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e/PG3976/BOM0a409301、host Linux/Python3.14、guest boot79a/JDK25.0.4。正式1964PT/53scope/旧個別17/190/工数null/QA051final保留を維持する。

## 事実と独立期待値

4348元6609 actual1はsignal前invariant拒否、元58917はUNKNOWN継続。4354元57474 actual0/privatef1ad8ea8：過去4336との差はAPI fd93のtarget/metadataだけ。4356元59442 actual0/privatecd2d8421：現在API93/96・Web110をcaptured fullFD内socketinode→固定role/app/同PID→loopback ESTABLISHED 5432/本人server逆向きTCPへ結合。旧TCP表未採取につき旧fd93の当時pool所有は未認定。現在一致を元失敗pairの証明へ使わない。

PT-OPS-POOL-FD-CAPTUREの独立fixtureはAPI2..8/Web1..2、明示した両向きTCP・inode/UID/GID・全descriptor値。境界外数、未知/余剰role・app/port/片端/別backend・重複/alias・不正UID・captured inode差・非pool全field差を拒否。server側inodeだけ変更する独立反例は旧bindで戻り値同一となる欠陥をレビューで再現し、修正前にBUG1352へ起票。修正後はserver PID/ticks/argv/authority/fullFD・対応server FD/逆向きendpoint/state/inodeを保持してkeeper/partial双方の二読で差を拒否する。生TCP timer/queueは全private保存しauthorityから分離する。

PT-OPS-POOL-BOUNDARYは全snapshotkey/DBrows/両端witness差を二読拒否し、再取得で合格化しない。PT-OPS-REJECTED-SPLITは各像を独立private file＋最終hash indexへwrite/fsync/dirsync、各file64MiB上限維持、二file目失敗/二回目bind失敗/証拠保存失敗を伝播。旧v1実proof75569 actual1はpairが64MiB上限超過して拒否像保存に失敗（BUG1351）、成功へ読み替えない。旧v2はstage41230 actual0のみ、proof未実施のままv3へ継承、旧file上書き0。

## 実行結果

`PYTHONPATH=tools/quality:tools/quality/vm/050_s1:<pyflakes3.4.0/runtime> python3 -B tools/quality/pg4370_pool_bound_qualification.py`：**17工具試験/FES0、host＋全4emitted静的0**（新14＋既現transport回帰3）。logSHA f36db75b9b239cb2a854197fc9557d60234aedae5cdfbc1adc92d40c00e1b0a9。Production PT追加0、coverage100や工程率へ加点しない。全host/source/hashは公開manifestで固定する。

4366v3 stage元69860 actual0、keeper647dd2d1/partial213f3a1e/postd64b8c58。**同artifact実無操作proof元60825 actual0/13:25:32Z**、全両端/元pair/全原値・新十Ref正常、signals0、全二像79b0d6f0/259ec27e保存。限定独立ultra reviewはserver-only反例・partial差・bind保存/分割伝播の解消を確認、新unsafe受入れ指摘0。実VM操作は親だけが実施、reviewはreadonly。

設計only PR139/main **6eae971276832c6d0cc9e29fbc18c5090d3cf6ad**（実施design e0c73db2e/隔離5094eca6d）remote確認済。実装/tools/evidence混在0。添付100件上限は保全しPR URLを記録する。公開evidence/provisional/PG4372-pool-bound-preparation-v1/manifest.json SHA **eff1abd79e9831181bce20b065e5474fe2165c03d8c27411f70567a173e6b0c2**、raw/credential/DB値公開0。

## 未完

新4368v3のowned Java→Python各一回/元transport実値回収・自然hostgate継承・同partial inspect/必要五停止/Caddy観測だけ/typed revoke全37保持・別freshpostは本資格では未実施。旧Roottimeout143/58917 UNKNOWNと区別する。Root性能原因BUG1332・新通常親真正DONE・当source native CRC/session・実Browser/CHR/F03/四counter100/451/trace/引継ぎは後続未受入。
