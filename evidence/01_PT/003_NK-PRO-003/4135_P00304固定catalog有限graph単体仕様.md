# P00304 固定catalogの有限graph分類・単体仕様

Program NK-PRO-003、WBS-P003-04。FIL001..009/UI237/SS333/411、BUG2718/YKT2359。

StorageIoException.preserveFatalは公開Throwable graphのcause→suppressed→SQLException.next順をidentity集合で有限巡回し、到達した同一Errorだけを非正常伝播する。provider文字列/graphを固定例外へ保存しない。独立期待値はテスト自身が生成する同一Error参照、固定message literal、三Reason literal、非fatal循環の正常return。expectedを製品methodで生成しない。

PT-STORAGE-GRAPH001: 全Reasonの固定message・cause/suppressed無し、reason/null境界。
PT-STORAGE-GRAPH002: direct/cause/suppressed Error identityと既cause/suppressed巡回順位。
PT-STORAGE-GRAPH003: SQLnext、cause/suppressedからSQLnext、循環/重複辺の有限終了。
PT-STORAGE-GRAPH004: 非fatal空/循環/null境界・同じ入力graphを変更しない。JDK memory objectのみ。

OwnedTransferDirectory.executeの三checked catchへ同helperを固定COLLISION/MISSING/UNAVAILABLEへ変換する前に接続する。正常理由・lock/finally・ResourceScope・実FS能力・publish/collision挙動・一度closeは変更しない。保持root/FD/native/FS依存の実caller PTはHOLD/NOT_RUN。helper UnitのPASSを三callerの実行合格へ算入しない。

ResourceScopeのprimary/secondary優先順位はSS333の例外規則がある。原ResourceScopeTest knownBodyFailuresは既suppressed Errorも固定IO化する独立期待値を持つ。したがって当処理はgeneric fatal guard横展開の非該当、use/acquire/handoff一切変更しない。元受入17を一括再認証しない。

事前source6f7、PG27678 before、source製造PG27680 exact inverse/configured GJF-CS0。現時点製品PT0・Maincompile0・coverage未測定。普通helper-only PTは次群でsource固定とRoot NullAway/静的解析・同run CRC/四counterを確認してから実施・記録する。実DB/VM/Root/実鍵/native/actual4/私有grant操作0、旧source成功の転用0、正式1964PT/53scope維持。
