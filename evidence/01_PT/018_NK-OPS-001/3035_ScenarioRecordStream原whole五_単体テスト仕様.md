# ScenarioRecordStream原whole五・単体テスト仕様

2026-10-31／PG-D970／NK-SCN-001、RD FIL/PER、UI234/237、SS322/323/333§5、PT-SCN008-W04/W05。Production6b53/normal14216固定、HEADde16961854da0e9cbf3818d971eb7b311814c8be・push35822真正0。群3374実leafP00806、開始1/3/7共有pp cap10。旧2366/2368は別sourceの履歴であり当sourceへ成功転用/加算しない。現在Main未測定/原Test五未登録を実registryで確認、全Main76行・Test全body/initializers/全FaultChannelと使うprotocolの当source既proofを確認。

原whole五/一suite：
- w04One201And10000RecordsMatchEveryGoldenByteAndIndependentDigest：1/201/10000record・4800*count最大48MB、入力clear後もimmutable保持、recordCount/byteLength/toString、全4800byteを手書きUIoffset oracleと比較しSHA256別蓄積、一byte余分もなし。caller channel保持。
- w04ImmutablePreparedRecordsSupportConcurrentIndependentChannels：自己8thread/16別channel、各三record・全byte/hash一致、executor/future全回収。
- w05PreflightRejectsNullCountSequenceAndInvalidLastRecordBeforeAnyIo：null list/element、0/10001、sequence2から開始、201件目の4097byte/改行/NUL不正bodyはfile生成前拒否、null channelNPE・own root空。
- w05PartialWritesRemainBoundedAndForceOnlyAfterAll4800Bytes：7byte分割600回超でもbuffer最大4800、全write後のforce(true)一回、caller channel開、独立hash一致。
- w05ZeroNegativeWriteIoForceClosedAndNonfreshChannelsFailWithoutImplicitClose：zero/negative/writeIOException/forceIOException、closed、position1/nonemptyはStorageIoException.UNAVAILABLE/cause0/suppressed0、期待size/force/caller保持。

独立goldenはproduction encodeをexpected生成に使わず、space4800にID71+index/sequenceindex+1/line42+index/narration/本文＋index/audio000をoffset0/12/18/26/164/4260へUTF8 literalで配置。SHA256は別MessageDigestから全期待recordを蓄積、Main digestからexpectedを逆生成しない。元Test/期待固定、不明なsource/runtime成功を加算0。

自己JUnit TempDirの公開fixtureだけJDK FileChannel open/write/force(true)/read/closeと普通のcleanupが発生する（実JDK filesystem/forceを隠さない）。storage FFM/native-gate/Linker/実業務root・原本・公開/rename/配備/permit/intent/DB/HTTP/JMS/VM/Root/Graph/秘密key0、cryptoは公開fixture SHA256だけ。Mainは借用channelへ書くがPathをopen/publish/deleteせず、Root/noargsや業務の真正終端を実行しない。no mapping/lock/truncate/transferというfault実装も全読、これらは呼ばれたらAssertionError。

Command python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg15886_scenario_record_stream_five_pt.py。JDK25.0.4/Java25 freshjavac -proc:none-Xlint-Werror、JUnit Jupiter5.13.4/Platform1.13.4/JaCoCo0.8.15、固定六normalJar＋外部依存・親180秒。c86d8e01 Main/dab5445d Testは現src/normal input/snapshot/Jar closureに完全一致することをbody前確認。protocol/StorageIoException/LargeResultContentの元Source proofは非再受入。

15888は同exec/CRC/session/当一Source一Code全四counter・四held六native trueprobe0を受動確認。期待coverage未実測、未達を除外/合成しない。15890で独立byte/hash/全五XML/安全境界を確認し、3036へ実日時・command・環境・actual exit/hash/関連BUGを記録。Failed/flaky/skipped/not-run合格0・Product障害は修正前915/916。正式1964/53・歴史17/190・工数null/QA051final/全451・安全HOLD維持。
