# BUG204/YKT160 bundle元inode横展開

正式認定: PT-WEB-20260919-02/source 0ca3aa9588fa480ccf4b3e4ff06561f627365e66/dev-foundation、2026-09-19 23:58:54～09-20 00:14:59 JST、Maven16分04秒/exit0。全1455 PT（80/74/660/241/359/41）・failed/error/skipped0、6 Java全4coverage100%、Production5静的解析未解決0、固定path3method限定review・coverage除外なし。15collector/38scopeと46負canary成功。PG175/176/177の16/8/16 PT・3部品を認定、BUG199～204/YKT158～160/SSC064～066完了。実archive生成/DB成功caller/7世代/親全体/実NK CHR/IT/STは未完了。実行環境・source/test/入力期待実際・hashは017/018各evidence/manifest.json。raw実行log SHA256=b777f9ea117c514d2ae78fcc402aaf9711147655a50df31024e6eeb47c0abf94。以下は探索時点の履歴であり、旧「未認定」は当時の状態。

2026-09-19。修正前反例 `/tmp/pgpt-bug204-red.log` は23:47:53 JST終了/exit1。Storage共通8は成功、新BAT268の1件は「例外が投げられない」で失敗。同期済partを退避し、native publish直前に同byte4fileを持つ別directoryを作ると、digest-only比較では元inodeを区別できたと誤認した。反例fixtureは公開合成byte/UIDだけ、実fileのrename/copyで再現する。

## 対象・非該当根拠

| 対象 | 確認・対応 | 再試験 |
|---|---|---|
| 新BackupBundlePublisher/ArtifactVerifier | force済directoryと全4fileの不変BundleSnapshotをphase間で保持。manifest hashだけでなく子dev/ino/nlink/size/mtimeとfile全9属性を照合。子ctimeだけrename許容 | BAT268実clone反例、metadata差分、BAT261 digest provider差、BAT272不変Map/NULL・旧readonly |
| BackupManifestPublisher | 元written snapshotをpublish後のsame inode/devとsize/mtimeへ照合、さらにreadback後全属性。変更不要 | BAT249の実part/公開先/子差替え、全新16回帰 |
| InspectorEnvironmentPublisher | expectedをpublishAs前から保持しexpected.samePublishedFile(published)、readback後published.equals再照合。変更不要 | replacementsAndRetentionと全PUB12 |
| DurableRecordFiles | 新規/再利用双方でexpectedを保持、公開後samePublishedFile、同snapshotでreadStable。変更不要 | namespaceAndReplacement/metadataAndFilesystemsと全BAT046～057 |
| OwnedTransferDirectory.publishChild | backup真正性を返さない低位能力。caller前後照合をSS333§7.5に明記。仕様をこえて単独成功をbackup成功としない | PDIR8と上記実clone caller反例 |
| public Reader/ArtifactVerifier | 同一観測phase内は元snapshotを再保持して比較。readonly観測だけでforce完了を主張しない。公開APIの入力/診断/IO期待値は維持 | BAT194～209/226～241全回帰 |

検査後の第三者変更を永続防止する保証へ拡張しない。callerのOS連続排他/actor停止は維持する。検索だけで完了にせず、上表全PTと全reactor/trace認定後にBUG204/YKT160を完了にする。現在は修正・再試験待ち。
