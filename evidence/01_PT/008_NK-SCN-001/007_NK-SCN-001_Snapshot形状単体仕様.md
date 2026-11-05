# Scenario Snapshot形状 単体仕様

Program NK-SCN-001 / ScenarioDetailSnapshot全record / FUN004/005・UI234§10/237・SS323/332§4.2/333・411/451・782。原PG17290/3370は成功だがSnapshot17L/4B covered、1L2B未達。未実行FILE/10001形状拒否を追加し同Source全体を検証する。既完了ScenarioDetailDeliveryは対象外で再実行しない。

|Test ID|ScenarioSnapshotShapeTest method・入力・独立期待|
|---|---|
|PT-SCN-SHAPE001|fileMetadataAnd10001RecordsRejectAtShapeBeforeAnyResultEscapes。合成FILE metadata/emptyrecordsとINLINE metadata/10001recordsはliteral IllegalArgumentException「invalid scenario snapshot shape」、元リストサイズ/末尾sequence不変。FILE入力は合成DTO/論理path/hashだけ、実file/hash/許可の証明なし。|
|PT-SCN-SHAPE002|nullMetadataListAndListElementsAreContractRejectionsWithoutNullNormalization。metadata/list/collection要素nullはconstructor invariant NPE拒否、入力リスト不変。NPEcatch/正常化なし。|
|PT-SCN-SHAPE003|zeroAndOneInlineRecordsKeepOnlyTheirOwnedImmutableSnapshot。empty/one INLINE、caller clear後も元record参照/metadata保持、固定bodyとredactedrecordCount文字列、戻りリスト変更不可。|

既ScenarioDetailSnapshotBoundaryTest全3 SNAPSHOTMAX001～003も同じexactTest sourceで選択。10000行のfirst/last ID-sequence-body/copy/immutability、途中201/5000/9999欠番、末尾4097文字の独立期待は3369そのまま。これは未達分追加後の全Source runであり、元成功確認だけの再演や旧exec合成ではない。期待値はliteral形状/件数/入力値/SS列上限、productioncodecはactualの検証側だけでexpectedを生成しない。

Fixtureはmemory DTO/List/Optional/固定UUID/合成hashと公開codec/semantic型だけ。実DB/filepublisher/filesystem/native/Root/VM/auth/session/鍵/credential/実network0、HELD四class依存なし。Nonnull/null要素/immutable copy/shape入口の不正を正常扱いしない。既Boundary3/Mainは不変更。

原PG18956 compile1（Sha256Hex privateconstructor誤用）とstatic前提guard1未実行をBUG2285/YKT2030へ修正前登録し、公開Sha256Hex.ofへだけ是正。他semanticfactoryと公開record契約を横展開照合。Mainbuild/NullAway/六SBはb093のPG18642/18648全input/JARpinで再利用。PG18960compile0/18958static後、source固定しPG18964全6/2class/単exec-session/正常MainCRC/全physical1/四counter100/HELD四probe0を独立post。元失敗と未実行を合格へ算入しない。結果/command/時刻/OS-JDK/source/exit/hash/BUGは008へ保存。親WBS/実file/owner/DB/CHR/V/正式451は未完。
