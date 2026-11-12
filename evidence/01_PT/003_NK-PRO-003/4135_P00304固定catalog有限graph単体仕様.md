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


source固定commit edaf641333266660ec79a6e070c98b7a79bbccac、独立sourcejoin [manifest](../018_NK-OPS-001/evidence/PG27684-storage-catalog-source-join-v1/manifest.json) SHA767f6b769022ae5484baf1a4ab2d49f963deb1471392230e6e4749f471631dc7。StorageIoExceptionへ既有限identity/cause-suppressed-SQLnext分類algorithmをmodule内実装、OwnedDirectory三catchへ既理由変換前call。元6f7へexactinverse/GJF-CS0。ResourceScopeはSS333明示複合優先規則により非該当、未変更。実Dir runtime/DB/native/Root/FS/actual4未実施・BUG2718OPEN、helperUnitは後続別価格。旧P00304/08受入は元source歴史で維持し新sourceへ合算0。 製品PT0、runtime/coverage未受入。


実行source f557e11ee0df831af5e5da14aa4d00250f981d0a / Production edaf641333266660ec79a6e070c98b7a79bbccac。PG27688元Root compiler compile→PG27689 import-only Test compile→PG27692独立preflight→1764a qualifier run→1767 independent post。実行command/cwd/start/end/exit/tool環境はPG27696のunit-/original-保存証拠とmanifest/files SHA256へ一意対応。

GRAPH001=fixedReasonsAndNullContract、002=directCauseAndSuppressedIdentityAndOrder、003=sqlNextAndMixedEdgesRetainIdentity、004=nonFatalCyclesAndDuplicateEdgesFinishWithoutMutation。新helper全4成功/FESabort0、独立PG27696/71e496cd：全3physical/2positiveCRC・package-info自然noCodeのみ、同exec全selected scope L24/M4/C2/B12を含む全counter100。RootそのままNullAway新Main2、PMD0/CS0/SB0/format0。初回Teststarimport1は未実行stageで訂正・Testのみ再compile、Maincompile不再演、旧静的失敗PG27690保全。新4定義はpublic memory graph/SQLnext/cycle/null/identity固定期待値、実Dir/root/native/FS/privategrant/actual4代替0。BUG2718三caller実runtimeは未実施OPEN、ResourceScope優先規則未変更。原190新0/正式1964-53/工数null。
