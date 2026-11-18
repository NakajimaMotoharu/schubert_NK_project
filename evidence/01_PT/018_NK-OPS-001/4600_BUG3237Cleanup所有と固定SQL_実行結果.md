# BUG-3237／3238 Cleanup所有と固定SQLの実行結果

Core ba13ded812907d1b60a2110ec88fbf8076101133、固定試験source 56ae8c9dc3b831c286c3b4f43c1fffc465408fd2、PG38729。CLNPORT001～009とCLNQUERY001～009の全18初回成功、F/E/skip/未実行0、21物理／19陽性CRC。対象2型の公開ABIは同一。NullAway、Checkstyle、SpotBugs0。PMD44はscopeごとの独立根拠で適用0。先行の非定数SQL案ではSpotBugs1件、動的PTを発行していない。

CleanupStepRepositoryの75L／7M／1C／28B／325Iはすべて到達。CleanupRepositoryの99L／10M／1Cと31Bは到達。両Repositoryの手書き8分岐の不足を解消した。元九つのSQL literalを保持し、残ったjavac defaultの1B／6I、SwitchMapの9Iを報告した。支援型・全module・全451は未成立。既execの結合、手動除外、実DB・削除は0。

資料PG38734は生成分岐とYKT-2683候補10型を個別収載。対象2型と既RunReferenceを確認。残7型には別所有境界、Root/HOLD、実測未実施を含み、横展開全体は継続。証跡 evidence/01_PT/018_NK-OPS-001/evidence/PG38734-f03-cleanup-raw-owner-proof-v1/manifest.json SHA256 06b502f2f7b0d0941bacb52bbb8b03fdc7c866dac5ec621a8cb0147292b87d0e。
