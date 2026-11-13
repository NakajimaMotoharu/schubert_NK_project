# BUG2794 manifest read strictcount/position/EOF source PG

NK-OPS-001/WBS-P018-02; SCM001..005/SYS002004/OPS009; UI251; SS3439.1/11.1・SS351451、YKT2399。保持fileの既存最大1MiB・root/current/selector/inode/全ownedclose/Hash正常結果/権限は不変更。初期channel位置0、positivecount==buffer.position、count<=実remaining、channel.position==total、EOF=-1かつbuffer不進行/位置維持を検査。従来MAX累計guardは既上限確認済before.sizeの増分前remaining検査に置換し冗長な到達不能assertを追加しない。

元全source byte inverse/GJF-CS0はPG28942、実Maincompile/NullAway/fullPMD-SB/通常PT/coverageは未実施。以下は独立literal故障port仕様であり実行成功に数えない。native/全StartupTestはHOLD、method部分抽出やRoot代替を使わない。

- MANREAD001: size2, initialpos0, read2/bufferpos2/channelpos2, thenEOF-1/bufferpos0/channelpos2 → continuehashandunchangedexistingallclose/inoderecheck（NOT-RUN）
- MANREAD002: initialposition1 → rejectbeforefirstread/ownedchannelclose（NOT-RUN）
- MANREAD003: size2, read2/bufferpos1/channelpos2 → rejectcount-versus-bufferbeforehash（NOT-RUN）
- MANREAD004: size2, read1/bufferpos1/channelpos2 → rejectchannelpositionbeforedigestupdate（NOT-RUN）
- MANREAD005: size2, read3/bufferpos3/channelpos3 → rejectdeclaredsizeoverrunbeforehash（NOT-RUN）
- MANREAD006: size2, read0/bufferpos0/channelpos0 → rejectzeroprogressnoinfiniteretry（NOT-RUN）
- MANREAD007: size2 fullyread thenEOF-2/bufferpos0/channelpos2 → rejectnoncanonicalEOF（NOT-RUN）
- MANREAD008: size2 fullyread thenEOF-1/bufferpos1/channelpos2 → rejectEOFwithbufferadvance（NOT-RUN）
- MANREAD009: size2 fullyread thenEOF-1/bufferpos0/channelpos3 → rejectEOFwithchanneldrift（NOT-RUN）
- MANREAD010: size2 read1thenEOF-1 withconsistentpositions → existingexactsizepostconditionrejects; no publishedhash（NOT-RUN）


借用Root/原本/実release/秘密/key/VM/サービスを操作0。BUG2794/16target YKT2399は修正sourceを保存しても再試験未完OPEN、原190/451/ITST/工数率不変。固定source/command/hashは後続sourcejoinへ追記。


source固定commit ae1f2b2eb9205af679b8fad522dc8aabc4ecff6a、独立sourcejoin [manifest](../018_NK-OPS-001/evidence/PG28946-manifest-read-source-join-v1/manifest.json) SHA9bd6a3a13d9268c93fd3f67c022b8d31fa7324073977c95421ad6c74e63b94a9。BUG2794StartupReleaseManifest.manifestに初期位置0/countとbuffer位置一致/実残サイズ内の増分/channel位置==累計/EOF=-1と不進行のstrictguardを追加。既1MiBcheckedsize前提の増分前残量検査で旧totalMAXguardを置換し冗長到達不能比較を追加0。元全sourcebyte逆変換/GJF-CS0、normalNIO/全保持inode/selector/Root権限/ownedclose順/Hash正常結果不変更。独立故障port10例は仕様だけNOT-RUN、Maincompile/fullstatic/PTcoverage未、実release/Root/nativeFD/key/VM/service0。BUG2794/横展開16target YKT2399はOPEN。 製品PT0、runtime/coverage未受入。
