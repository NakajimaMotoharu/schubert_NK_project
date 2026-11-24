# BackupManifestCodec 固定goldenの現候補結果

PG44124、`062a9f5e779e3184b3e87faaec29e5b1386b5415`。正規Batchの対象にPT-BAT-186～193を8件実行し全成功。失敗・エラー・skip各0。独立goldenと同一965 byteを専用scratchに保存しSHA-256が一致した。旧PT-BAT-187の成功は別保存し、現候補での新規資格へ二重加算しない。

生計測は対象一物理で行77/79、メソッド6/7、クラス1/1、分岐12/12。private namespace constructorの未到達2行・1メソッドは測定に残す。実Backup、DB、実原本・保持の操作0。451と正式受入は未成立。

[単体仕様](035_NK-BAT-001_backup_manifest_codec_単体テスト仕様書.md) [証跡](evidence/PG44124-current-backup-manifest-codec-synthetic/manifest.json)
