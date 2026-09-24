# NK-OPS-001 固定設定実file読取単体テスト仕様書

Program NK-OPS-001。Class/method `ServiceConfigFiles.read/checked`。RD SYS-002/004、UI243/253、SS311/342/343 §2/4、PG-D-275。対象は固定の非秘密`/etc/schubert-nk/common.yml`とAPI/Web設定を、保持inodeから上限付きで読む境界である。試験fixtureは隔離temp directoryの公開値のみを使い、OS account/ACL/filesystem、envとcredential、複数fileの原子的配布、外部process起動・readinessは認定しない。

| Test ID | 目的・事前条件/fixture | 入力・操作 | 独立期待値・根拠 |
|---|---|---|---|
| PT-OPS-CFGFILE-001 | root0750、file0640、公開ASCII YAML3件 | API/Webの固定名読取 | 手書きliteral UTF-8 `common.yml`と`api.yml`/`web.yml`の内容がそれぞれ完全一致。Productionで期待値を作らない |
| PT-OPS-CFGFILE-002 | 同fixture | API欠落、symlink、directory | 全て固定`StorageIoException(UNAVAILABLE)`、内容・path非公開。SS343固定名/NOFOLLOW |
| PT-OPS-CFGFILE-003 | 同fixture | 0/16384/16385 byte、不正UTF-8、file0600 | 1～16384 byteだけ、厳格UTF-8のみ受理。境界はSS343 §4の16KiBから独立算出 |
| PT-OPS-CFGFILE-004 | 同fixture | hard link、root0700、所有者不一致 | root:schubert0750/file0640・単一link・同deviceだけ受理。UI243/SS343 literal |
| PT-OPS-CFGFILE-005 | inode metadataの手組差分 | owner/group/mode/nlink/dev/ino/size/ctimeを各1項目欠落/変造 | どの差分も固定非成功。実Linux `unix:*` の型とUI243 mode値を独立転記 |
| PT-OPS-CFGFILE-006 | 同fixture、32並行 | null各境界、Contents不変条件、所有close失敗 | nullはNPE、所有close失敗は固定非成功、並行読取は同じliteral。NPE catchで正常化しない |
| PT-OPS-CFGFILE-007 | package内Io故障portと実保持inode | 読取中root/file ctime drift、初回/終端size、0 read、短読、上限超read | 全て固定非成功。属性呼出順・byte上限はtest側faultで独立指定し、production methodで期待値を生成しない |

正常・境界・異常・null・例外・並行を検証。再送は読取専用処理に非該当。coverage除外なし。実行command、branch/commit、日時、coverage、結果、BUG、証跡path/hashは065と同Program `evidence/manifest.json`に記録する。
