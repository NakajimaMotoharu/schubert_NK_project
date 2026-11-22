# Maven Wrapper配布物照合

WBS-P018-02/2、RD171 SCM-004/005、SS352 §13、`.mvn/wrapper/maven-wrapper.properties`。PG42734は `6646eb7bde4b4ce0ae7d53cb44492258e4544291`、配布ハッシュ設定 `d47331e1ce`、dev-foundation、JDK25.0.4／Maven Wrapper3.3.4で実行した。

| 試験ID | 操作と独立期待値 | 実行結果 |
| --- | --- | --- |
| PT-OPS-MVN-WRAP001 | 公式配布ZIPと別配信元のApache公開SHA-512を照合する。ZIPから算出したSHA-256を正規propertiesに固定した状態で、空のMavenユーザー領域から `./mvnw --offline --version` を実行する。終了0、固定版3.9.12、インストールされた起動ファイルが検証済みZIPと一致。 | 合格。終了0、Maven3.9.12・JDK25.0.4、起動ファイル一致。 |
| PT-OPS-MVN-WRAP002 | 別の空領域でpropertiesの期待値だけを全桁0に変え、同じZIPを `./mvnw --offline --version` に渡す。終了1、展開・起動前に拒否され、インストール済み実行ファイル0。 | 合格。終了1、起動ファイル0。 |

検証済みZIPを一度だけ渡すローカルのダウンロード代替を使い、新規キャッシュと既存キャッシュの混在を避けた。製品試験・製品coverageおよびWindows起動の実測は今回対象外。新規展開時の検査であり、展開済みキャッシュの整合確認は別群。実行時刻・処理別終了値、原証跡SHA-256、ZIPとpropertiesのSHA-256はmanifestに保存した。[PG42734](evidence/PG42734-p01802-maven-wrapper-distribution-checksum-v1/manifest.json)

PT-OPS-MVN-WRAP003／PG42736。既存Linux cacheを読み取り、照合済み公式ZIPの96ファイルすべてのSHA-256と `bin/mvn` の実行可能性を比較した。96一致、欠落・不一致・特殊ファイル・未識別の追加ファイルは0。Wrapper自身の追加管理ファイル `mvnw.url` は名前だけ照合した。Maven再実行とキャッシュ書込は0。[PG42736](evidence/PG42736-p01802-maven-wrapper-existing-cache-v1/manifest.json)
