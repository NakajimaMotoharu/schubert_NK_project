# NK-BAT-001 root manifest公開単体テスト仕様書

2026-09-19、SSC064/PG-D-175。状態: 仕様先行、全件not-run。正式1415 PTへ加算しない。

対象 `.batch.file.BackupManifestPublisher` のconstructor/createと全内部method。RD141 BAK001～008/RD171 BKO001～008/OPS009、UI251、SS311/341 §6.8/343 §5.3。生成実archive/DB/7世代の完成は対象外ではなく別未完了作業。

## Fixture・独立期待値

実Linux temporary directory/保持FD/no-replaceを用い、root UID0とbackup UID2000/GID2001はmetadata portによる合成と明示する。既存read-only BackupArtifactFixtureは変更しない。入力manifestは公開合成fixture、expectedは手書き `src/schubert-nk-batch/src/test/resources/backup/artifact-manifest.json`（964 byte、SHA256 bd608252091beeda64978c96a85107bd329c56f4222cb0a21c39b868af45c370）を利用し、production encodeをexpectedに使わない。固定part UUIDを使用、root borrowed・新file0600・失敗時部分保全・全所有resource解放・buffer全zeroを毎ケース確認する。IO出現点inventoryは実装とは独立に確定して追加する。

| Test ID (PT-BAT-) | method/目的 | 入力・操作/期待 |
|---|---|---|
| 242 | independentGoldenPublication | 正常claimのcreate後、MANIFEST byte/hashが手書golden一致、UUID.part消失、他file不変 |
| 243 | privateCreationOwnership | CREATE_NEW mode0600・root所有で開始、chown/truncate/unlink禁止、借用root継続 |
| 244 | rootAndChildAdmission | UID/GID境界、不正root/子type/mode/owner/device/ACL/RW、既存子のみ、固定失敗 |
| 245 | metadataNullTypes | 全9fieldの欠落/null/誤型、null map、各観測段で拒否 |
| 246 | filePermissionsAndLinks | regular0600/root/nlink1、初期size0/最終長、inode/device等不一致を拒否 |
| 247 | writeProgressBoundaries | 分割write、0/負/過大count/position不一致、size前後、force/close異常で非成功 |
| 248 | readbackAndIdentity | 分割read、短縮/過長/0/位置不一致/内容違い/size/前後属性違いで非成功 |
| 249 | namespaceReplacement | part/公開先/子/rootの差替え拒否、renameのctimeのみ許容、読取中ctime変更拒否 |
| 250 | collisionAndPartRetention | UUID.partとMANIFEST既存衝突、上書き/自動削除なし、失敗後現物保全 |
| 251 | everyIoFailure | 独立IO inventoryの全出現点へIO注入、非成功・解放・安全diagnostic |
| 252 | deadlineAndInterrupt | 30分未満/一致/逆転/wrap・各境界の割込、flag保持・非成功 |
| 253 | compoundAndBufferWipe | unknown body/close同identity、known body＋unknown cleanup、固定secondary・全buffer消去 |
| 254 | nullAndClosedContracts | 全API null、閉じたroot、失敗時borrowed寿命、NPE正常化なし |
| 255 | concurrentNoReplace | 同一/別instance・同part/別partで衝突、成功1件・既存byte不変 |
| 256 | nativeIoAndFactory | 既存NioIoの実write/read/fsyncとpublic factoryの境界、synthetic rootと実配布を区別 |
| 257 | independentPublicationTrace | 実公開結果の非秘密byte数/hash/結果を固定oracleに照合、collectorへ追跡 |

## 実行・証跡契約

JDK25.0.4/Maven3.9.12、dev-foundation、対象commitは実装後記録。選択testはResourceScopeTest,BackupManifestPublisherTestをbatch -amでtest＋JaCoCo0.8.15 report＋SpotBugs4.10.4.0 check、正式は新IDで単一clean verify。line/method/class/branch各100%、failed/error/skipped/not-run0を完了条件とする。探索結果だけで正式認定しない。実行結果054、manifestは既存017/evidence/manifest.jsonへ追加しrun日時/OS/tools/source/command/exit/独立expected/actual/coverage/hashと関連BUG/SSCを記録。secret/raw token/session/key/dumpを保存しない。
