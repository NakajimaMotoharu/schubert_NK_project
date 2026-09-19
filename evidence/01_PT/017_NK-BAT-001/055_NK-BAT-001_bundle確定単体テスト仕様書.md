# NK-BAT-001 backup bundle確定PT

SSC066/PG177、2026-09-19、実装前・全not-run。対象BackupBundlePublisherの全constructor/publish/force/guard/NioIo、BackupArtifactVerifierのpackage内forcePending/verifyWithinと共通engine、BackupManifestReader.readWithin。BAK/BKO/OPS009/UI251/SS311/333§7.5/341§6.10/343§5.3。

独立fixtureは既存手書artifact-manifest.json（964 byte、SHA256 bd608252091beeda64978c96a85107bd329c56f4222cb0a21c39b868af45c370）と公開ASCII3file（26/35/32 byte、PG166の固定hash）。expected生成にproductionを使わない。実Linux保持FD/rename/fsyncとsynthetic root0/backup2000:2001を区別する。sourceはclosed archiveを想定し実DB dump/秘密archiveを使わない。旧read-only fixtureは変更しない。

| Test ID (PT-BAT-) | method | 目的/入力・操作/期待 |
|---|---|---|
| 258 | verifiedDurablePublication | part4file→final同inode/byte/hash、partなし、manifest digest固定値、親借用継続 |
| 259 | forceOrderAndRetainedInodes | 全file read/hash後に同保持entryでforce→close、全4完了後子sync→publish→親sync→再読 |
| 260 | pendingContentAndMetadata | 4fileの改変/欠落/追加/属性/ACL/owner/device不正はrename前失敗・現物保全 |
| 261 | finalManifestAndArtifactChecks | rename後manifest/3fileの改変・同名別inode・正規claim変更を検出し非成功 |
| 262 | forceSizeAndNullBoundaries | writer前後size違い・null writer・open/force/close異常、内容writeなし |
| 263 | everyIoFailure | 独立IO inventoryの全出現位置で失敗、rename位置前後で残先を照合・owned leak0 |
| 264 | unknownAndCompoundFailures | unknown body/cleanupの同identity/優先順位、固定suppressed・raw診断なし |
| 265 | deadlineAcrossPhases | 単一開始tick、phase入口とforce中/最終IOで30分一致・逆転拒否/未満・wrap許可 |
| 266 | interruptionAcrossPhases | IO/clock境界で割込、flag保持・非成功・資源解放 |
| 267 | existingFinalAndMissingPending | final衝突時両方不変、pendingなしはMISSING、final再利用を推測しない |
| 268 | namespaceReplacement | 保持part/子/root namespace・rename後の再保持で入替え検出、部分保全 |
| 269 | nullAndOwnerContracts | 全constructor/API null、UID/GID0/範囲外・許容1/最大、closed root |
| 270 | concurrentPublication | instance直列・caller外部排他、同bundleの重複は成功1/次はpendingなし、byte不変 |
| 271 | nativePortsAndFactory | 実IO READ/WRITE非truncate/fsync/dir列挙、factory非root拒否、合成入場と実配布の区別 |
| 272 | readonlyCompatibility | 既存Reader/Verifierのfinal限定・無mutationを維持、package forcePendingに明示forcer必須 |
| 273 | independentBundleTrace | 実final byte/hash・force数/公開/同期を固定literal traceへ照合しcollector検証 |

JDK25.0.4/Maven3.9.12、dev-foundation、選択test→単一clean verify。同じclock/開始tickを全phaseへ渡すことをcounter/期限反例で確認する。class/method/line/branch100%、NULL/例外/境界/並行/再送不確定の独立assert、静的解析0。失敗/skip/flaky/not-runを合格にしない。実行command/対象commit/時刻/OS/exit/BUG/coverage/hashは056結果と017/evidence/manifest.jsonへ記録。正式認定前は部品・完成割合へ算入しない。
