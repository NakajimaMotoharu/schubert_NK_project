# P00806 保持reader・4800record・本文delivery 原4source契約

NK-SCN-001。対象source/hash、承認設計commit/hash、独立期待値/TestIDは [PG26890](../018_NK-OPS-001/evidence/PG26890-scenario-reader-contract-v1/manifest.json)。

- P00806-PG01 / ScenarioDetailDelivery.deliver/fileResponse / PT-SCN-008-R01..R03: Validatedimmutable snapshot<=200 inline/no publisher, 0/1/199/200/201/10000 boundaries; header256+DATA1728+200x4800=961984 under1M. >200 publisheronce borrowedoriginalimmutablelist/time, descriptorcount equals snapshotcount, project explicitDATA offset1328mode/1329UUID/1365path/1621size/1633SHA/1697recordlength/1703count, FILErecordsnone. Failed/null/mismatchedpublisher no fallback/retry/delete. Callback is public syntheticpublisher only, no realcontenthash/lifecycle proof.

- P00806-PG02 / ScenarioRecordStream.constructor/byteLength/write/encode/toString / PT-SCN-008-W04/W05: Immutable nonnull1..10000 rows, whole sequence plus every4800record validation beforeI/O includinglast4097/invalidcontrol; byteLength4800xcount withoutwhole48Mbuffer. Fresh callerownedchannel position0 size0, shortwrites loop/zero-negativefail, perrecordSHA, force(true) afterallrecordbytes, no implicitclose. Callerdata preserved, toString countonly. Independent peroffsetgoldens andseparateSHA. Synthetictempfiles only; parallelTestunbounded invokeAll/get andExecutorclose violates finitequality, BUG2681 beforefix; completeTest5 must befinitebeforeadmission.

- P00806-PG03 / LargeResultReader.readScenario/verifyDirectory; ScenarioRecordReader.read/scan / PT-SCN-008-RD03/RD04/RD05: Realretainedroot/readiness/accessexternalHOLD. WebLargeResultReader validates root/date ownergroupmode andheldready regular/nlink/size before+aftercallerownedchannel; no pathescapes/mutation. PureRecordReader borrowedfreshchannel pos0, first4800boundedscan exactEOF/hash BEFOREdecode, rewindonce andrescan+rehash bytesactuallydecoded, whole sequence thenimmutablelist. Neverreturnpartial; malformedreserved/required/UTF8/NFC/sequence withvalidhash rejected, badhash precedesdecode, null/nonfresh/closed/zeroIO/seekfail/mutatebetweenpasses fail andneverclosecallerchannel. FullRecordReader4 uses exclusively JUnittempSynthetic48Mfixtures andhandwrittenUI234bytes; effects disclosed, not nofileactions.

P00806 own4全文/SS3334～7/R01～03/W04W05/RD03～05対応。PG26890 6aa77727 metadata0、Deliverywhole3/Streamwhole5/Readerwhole4＋literalFixture全文確認、実Root/native LargeResultReaderwholeだけHOLD。Reader4/Stream5はJUnit所有一時fileを作成・後cleanupし48MBsynthetic bytesを扱う事実を明示、実原本native/cohort/権限操作へ拡張0。BUG2681/YKT2360はStreamTest一owner無期限invoke/get/TWRを修正前起票。

実行: `python3 -B evidence/01_PT/018_NK-OPS-001/input/1384_scenario_reader_contract_audit.py` metadata終了0。新規製品PT/coverageなし。原/1の準備だけ、原/2・451・元190未受入。独立期待値は公開設計の固定境界・順序・後条件に基づき、production methodで生成しない。正式1964PT/53scope・工数null。

## BUG-3918 並行試験の終了診断

- PT-SCN-008-W04 (並行)。同じprepared値から16個の自分で所有する一時channelへ書く。各3件の固定4800 Bレコードが独立した文字列・byte位置と一致し、独立SHAが一致する。元の他4件はPG44776の履歴に分離。
- PT-SCN-008-C03 (3件)。100予約の境界通過は1件のみ、呼出側monitor保持中も新規予約・snapshot・retain・closeを実行でき、8回のclose/retain競合はどちらが先でも予約を1回だけ精算する。入力と数値期待は既存試験を使用。
- PT-SCN-FIXTURE-WORKER001／002。JDK ExecutorServiceの合成代理で、停止要求から10秒待機の順序、停止失敗単独時の例外、元assertionがある場合の1件の抑制、割込み原因とflagを独立に検査する。実workerサービス・実root・DBは使わない。
