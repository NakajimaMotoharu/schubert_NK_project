# ScenarioSnapshot 現codec依存後の単独再認証仕様

Program NK-SCN-001、WBS-P008-05、ScenarioDetailSnapshot.<init>/toString、RD FUN004005/DAT009、UI234/237、SS323/332 §4.2/333、887/19800。原群.5/1.5/4pp cap5、元price・criteria不変更。既PG18964六whole(18L2M1C6B100/coreb093)と原Testを保持。現Main28af/normal19740のProtocol改修により旧execに実在する五codecclassのCRC差が確認されたため、現sourceの同じ六を再認証する。新規機能/新Test/新成分/原80追加完了へ加算しない。

fixtureは既ScenarioSnapshotShapeTest（三）とScenarioDetailSnapshotBoundaryTest（三）の全@Testを不変更で使用。全文静的確認済: typed metadata/record/codecとJDK List/Optional/UUIDのheap処理だけ。File ID/relative path/zero-SHAは型形式の合成値、ファイルを生成・読取・hashせず、HMAC/鍵/DB/auth/session/Root/VM/停止や再送を行わない。現Normal API/protocol JARをそのまま使用、private method抽出や同型replicaなし。

| Test ID | class/method | 独立期待値と不変条件 |
|---|---|---|
|SNAPSHOTMAX001|ScenarioDetailSnapshotBoundaryTest.snapshotMax001MaximumRowsRemainImmutableAndKeepLastRecord|明示1..10000 sequence/row-id/body、先頭/末尾literal、caller変異非影響、record list変更拒否|
|SNAPSHOTMAX002|ScenarioDetailSnapshotBoundaryTest.snapshotMax002InteriorAndTailSequenceGapsRejectWithoutChangingCaller|index201/5000/9999で明示sequence gap、LayoutValidationException、caller10000/同bad object不変|
|SNAPSHOTMAX003|ScenarioDetailSnapshotBoundaryTest.snapshotMax003TailTextPastWireBoundRejectsBeforeSnapshotEscapes|末尾本文4097byteでFieldEncodingException、caller配列/先頭/末尾不変。4096wireboundはSS323の独立値|
|PT-SCN-SHAPE001|ScenarioSnapshotShapeTest.fileMetadataAnd10001RecordsRejectAtShapeBeforeAnyResultEscapes|FILE deliveryと10001件を固定IAE/文言、INLINE上限10000とsize/modeの短絡全条件を区別|
|PT-SCN-SHAPE002|ScenarioSnapshotShapeTest.nullMetadataListAndListElementsAreContractRejectionsWithoutNullNormalization|null metadata/list/elementはcaller nonnull契約エラーとして拒否、NPEを正常化せずcallerList1不変。Main NullAway/NullMarked契約はnormal19740で既成立|
|PT-SCN-SHAPE003|ScenarioSnapshotShapeTest.zeroAndOneInlineRecordsKeepOnlyTheirOwnedImmutableSnapshot|empty/one、metadataとimmutable record参照保持、callerList.clear非影響、redacted件数toString、返却List変更拒否|

Expectedはtyped snapshot/production encodeから生成せず、元固定scalarと原schema/SSの上限・順序・0/1境界・例外classで独立作成済。不変oracleを新codecに合わせて書換えない。Main/Test/sourceとTest gitblobは既sourceと同一、依存currentCodecだけを切替。API/Protocol library/tool versionsはnormal19740 actualhashで固定、Gson2.14.0/JSpecify1.0.1/error-prone annotations2.50.0は同一toolchain依存で新規取得・version変更なし。

入力工具001のprofile snapshot_requal: prepare19810/static19812、sourcefreeze後unit19818を一度、post19820（producer/verifier Git artifact引数を明示）。六Test・2suiteのfound/started/succeeded/FESabort、whole normalphysical1/CRC/単exec-session/LINE18 METHOD2 CLASS1 BRANCH6全100と全present exec-core ID current一致/HELD四0を独立照合。元18964のexecと合算しない。全argv/日時/OS-JDK/branch/commit/終了/各hash/coverage/BUGは010/888-889とmanifestへ。静的raw/適用性も個別記録、suppress/除外/未実行をPASS扱いしない。

未受入=実DB read transaction/認可・Snapshot抽出/正規large-file生成・転送/Root/VM/native/CHR/全source451/正式1964-53/IT-ST/親WBSと第一V。今回のheap再認証をこれらの成功へ拡張しない。

Coverage分母は通常normal class一個の全physical CRCを対象とする。標準JaCoCo0.8.15のrecord生成equals/hashCode/accessor等の自動filterだけが働き、明示Sourceのconstructor/toString二methodは18line/6branch全対象。手動method/class除外・到達不能設定なし。OS/JDK/own tmpのallowlistだけを原newrun JUnitXMLからenvironment.safe.jsonへ保存。JUnit engine report三（Jupiter六/Vintage零/Suite零）、選択Test class二・method六を区別する。環境捕捉の最初の草稿で二classを二reportと誤認したassertは、Product終了/件数/品質に影響なしで三実report+六case集合へ訂正した。空engineはskip/not-run合格に加算しない。他System property/私有環境は出力しない。
