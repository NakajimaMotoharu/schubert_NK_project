# Morning保持owner・関連33実行結果

897/PT-OPS-RETAIN3396-001/WBS-P017-12.03。**PG3396/exec65448 actual0/Maven0、33case/8suite/FES-flaky-notrun0**。新Testは保持ownerの一methodだけ、他32は関連既存caseの再検証であり新規加点しない。

fixed snapshot4a75683def3480f3c0db8c359084a4419489dec0、archive de8328784b857ce223c7ee5903567421a35a7b4e1ecf987c6cb6bfe1faf75053、2026-10-15 14:18:05.935408～14:20:43.083302Z。aru固定JDK25/Maven3.9.12、原agent/同six module format/compiler/NullAway/SpotBugs0。これは未分類PMD2220/Checkstyle645を含む静的全gate合格ではない。

実caller FileLock→main interrupt→retainがflagをclear→別processから二度lock取得不可・子非終端→owned Process TERM→10秒内exit143→正常帰還marker無し/err空→別FileLock実取得、という全assertを実JUnitが正常完了した。143は意図したprivate helper子の終端であり、Production Root/Mainの中断を成功へ読み替える結果ではない。private実装reflection、Root/Unit/DB/Backup/ADMIN/VM操作0。

全1643Mainとresource/meta/debug memberは既真正全3706の全六Jarと完全同byte。payload SHA1f69ae7e8ece32f7017bc4cba2e199e384d1dd94d5ec4d1de1359d7a2008bdcb、server manifest7a0270494bda1de75e0cbaa6ddbb0918fa43a32300da90124179366bfcc7a4f6、Maven log c8123e33fbfddb44fe24ca3bfd89e8a2bab127834330c97470a2e64d7c6dd7da。公開`evidence/provisional/PG3396-retain-owner-related/manifest.json`（3bcc4763a8eae110ff44bd0a24d118db78b13516d432b30cfe3ffeb2f21c6f08）に各原XML/coverage/static/Jar hash・一Test source SHA・全結果を収容。私有原本はlocal pg3396-retain-owner-related-v1、aru runs/PG3396-related-v1/source-PG3396-related-v1。

対象retain methodの実counterはLINE covered3/missed0、METHOD covered1/missed0、INSTRUCTION covered7/missed0。無限保持の通常back edgeを実行して観測したもので、人工的なreturn/終了branchをMainに追加していない。class全体や全PGPTの100%ではない。

必要な一全体3707/543と同source native再資格はこの結果時点では未実行。既全3706へ1を算術加算して全体合格にせず、全体/独立/同28byteが成立するまでglobal残601L115M0C466Bの更新を保留する。正式1964PT/53scope、個別17/190、工数null、QA051final保留は不変。

新whole工具の最初のpure preflightは内部late-binding marker c/dの衝突で拒否された（新未実装工具TDD、外部job未発行・成功加点0）。既builderと異なるf0/e1 markerへ変更後、実hashに3706を含む反例でもdigest不変・actual count3707/543・独立batch1303/174/568を純二で確認した。hash/digestを数値置換して新しい成功を作らない。
