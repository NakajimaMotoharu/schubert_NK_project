# Backup原本工具metadata境界（PG2122、未実行）

NK-BAT-001/MorningBackupArtifacts.requireDirectoryMetadata・requireFileMetadata・requireToolMetadata・requireNoAccessAcl、BAK/BKO/UI251/SS341343、PG-D415/WBS-P017-03。既承認role/mode/uid/gid/link/size/ACLのliteral値を独立oracleとする。Productionの期待値生成/秘密credential/native authority偽装なし。

PT-BAK-2122-001：directory0/最大size・links2/9正常、五項一項ずつ違反/null拒否。002：file size0/1/4096正常、mode/uid/gid/links/負size/4097/null拒否。003：tool644/755・size1/268435456正常、七項mode/owner/group/link/zero/negative/268435457/null拒否。004：空ACL正常、null/非空IOException・元byte非変更。native前後チェック/IOexception/並行/replayは当pureguard外で後続実証、全4counter100へこの限定結果だけを使わない。

群0559凍結.5/1.5/4共有pp、所属訂正は費用移転なし。実command/env/source/coverage/XML/hash/exitは限定manifestへ保存するまでNOT_RUN。Production変更の必要fresh全回帰/native/正式451/CHR/全品質は別未受入。
