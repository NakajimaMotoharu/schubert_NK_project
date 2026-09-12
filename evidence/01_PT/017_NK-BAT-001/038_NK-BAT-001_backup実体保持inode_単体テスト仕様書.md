# NK-BAT-001 backup実体保持inode検証単体テスト仕様書

PG166/SSC059先行4da9e96b。BAK001～008/BKO001～008/UI251/SS311・341 §6.5・343 §5.3。PG165正式09/source89e97bdc凍結中の仕様先行、未実装/未実行/認定0。

| Test ID | class/method | 目的・事前条件/fixture/入力/操作・独立期待値 |
|---|---|---|
| PT-BAT-194 | BackupArtifactVerifierTest.trustedBundleAndManifestDigest | 公開合成3fileと独立MANIFEST literalを正規4fileへ配置し、期待MANIFEST SHA256/sizeと実返却を照合。実dump/age妥当性の証明ではない |
| PT-BAT-195 | BackupArtifactVerifierTest.completeFileSetAndCanonicalName | 未知/欠落/重複/null entry、part/別run名、余分な5件目を拒否。親の他generationは保持 |
| PT-BAT-196 | BackupArtifactVerifierTest.directoryAndOwnerContracts | 親/子のUID/GID/0700/type/links/device/readonly/euid0・不完全属性/負数/NULLを各位置で拒否 |
| PT-BAT-197 | BackupArtifactVerifierTest.perFileMetadataAndAcl | 4fileごとdump専用所有/root所有、0600/regular/単一link/同device/size、ACL44byte/異常/nullを個別検査 |
| PT-BAT-198 | BackupArtifactVerifierTest.rootAndChildRebinding | 親held snapshot・子の親からの再openを別観測し、子名差替え/親属性変化/closeを拒否 |
| PT-BAT-199 | BackupArtifactVerifierTest.eachFileReplacementAndMutation | 各fileの読取前・途中・最終再保持時にbyte/size/mtime/ctime/ino/権限を変更、実inodeで保全拒否 |
| PT-BAT-200 | BackupArtifactVerifierTest.sizesShortLongAndZeroRead | channel前後size、正確な残長/EOF、短縮・余分byte・0readを別位置で生成し無限loopしない |
| PT-BAT-201 | BackupArtifactVerifierTest.independentHashAndGoldenMismatch | 各3filehash1byte/manifest同長改変/別canonical/run・独立期待byteを検査、actual outputとexpectedの起点を分離 |
| PT-BAT-202 | BackupArtifactVerifierTest.streamingBoundaryAndLargeFile | 65535/65536/65537と複数bufferの公開合成byteに独立SHA256、long残量/境界を確認 |
| PT-BAT-203 | BackupArtifactVerifierTest.everyIoFailure | 正常実走から観測した全IO/native/clock/digest call数を別手書mapと照合し、全位置で故障発火・資源0・file不変を再試験 |
| PT-BAT-204 | BackupArtifactVerifierTest.resourceClosureAndSuppression | 全channel/DirectoryStream/entry/子close位置、primary IO/Runtime/Errorとcleanup IOの複合失敗を再現、fixed cause/suppressed |
| PT-BAT-205 | BackupArtifactVerifierTest.timeAndInterrupt | 30分未満/just/超/逆転/wrap、開始/各読取境界/最終割込、flag保持と未成功を確認 |
| PT-BAT-206 | BackupArtifactVerifierTest.providerNullRuntimeAndRedaction | provider失敗/null、dependency/manifest/entry要素null、未知Runtime/NPE/Error identity保持・raw秘密診断を出さない |
| PT-BAT-207 | BackupArtifactVerifierTest.borrowedRootOwnershipAndClosed | borrowed rootを閉じず操作後も使用可、既close root/子開閉不明は拒否、成功前の所有全close |
| PT-BAT-208 | BackupArtifactVerifierTest.concurrentSerializedAccess | 同instance64呼出しは直列、返却digestの独立一致・他generation非干渉、並行故障から資源漏れなし |
| PT-BAT-209 | BackupArtifactVerifierTest.readOnlyNoMutationInventory | read/open/metadata/list/close以外のmutationをfail-fast portで禁止し、全file byte/mode/名前不変・固定診断証跡を照合 |

Fixtureは公開合成byteのopaque3fileで、DB dump/有効tar/age暗号化成功を偽装しない。新fixtureのMANIFEST literal・実3hash/sizeをProduction実装前に別計算で固定し、Production encodeでexpectedを生成しない。全call map/EOF位置と期待順は実測数へ合わせずNIO/保持inode設計から独立に作る。metadata portがroot UIDを合成する非特権PTと実Linux FD/byte/hashを区別し、本番root/NASは後続Linux ITの必須確認。

Production全class/method: BackupArtifactVerifierの公開constructor/verify、非公開IO/digest/時計constructor、snapshot/集合/再binding/streaming/hash/安全close/guard/NioIoの全method。所有resource/collection null契約、全branch/line/method/class100%、NullAway/SpotBugs/Spotless・失敗/skip/flaky0を必要とする。除外追加で代替しない。関連不具合は修正前915/共通原因916、設計変更はSSC059へ記録する。

実行は421 Java25/Maven、batch -am選択PTと全module clean verify。対象commit/branch/開始終了/OS/JDK/tool/command/exit/4coverage/入力・独立期待とactual・関連BUG/SSCを039・evidence/manifest.jsonへ保存し全file hashで対応付ける。raw data/archive/credential/秘密key/token/sessionをGitへ保存しない。未実行分は不算入、artifact verifierのPASSを実backup/DB成功/親/PGPT/IT/ST完了としない。
