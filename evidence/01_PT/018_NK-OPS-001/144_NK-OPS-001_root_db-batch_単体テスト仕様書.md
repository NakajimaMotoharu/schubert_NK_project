# PG311 root db-batch 読取 PT（暫定）

Program NK-OPS-001 / RootBatchCredentialReader.read・inspect・NativeIo。RD DAT009/OPS009、UI251、SS341/3436.15、SSC094、PG311。既存非root readerと通常5秘密catalogは不変更。

| Test ID | 入力・操作/fixture | 独立期待値・根拠 |
|---|---|---|
| PT-OPS-RBCR001 | public UTF8 `PUBLIC_é\n`、1/65536byte、chunk2 | literal char[] `PUBLIC_é`、LF除去、所有buffer全zero、全channel/entry閉鎖。SS343既存UTF8 password codec |
| RBCR002 | null port、null channel、db-apiだけ存在 | nullは契約拒否、固定db-batch以外を読まない、資源漏れ0 |
| RBCR003 | directory/file全metadata欠落・型誤り・invalid、ACL/readonly/fs/UID/dev異常 | root:root0500/0400、single-link、readonly tmpfs、ACL0・同device以外拒否 |
| RBCR004 | baseline全IO eventへIO/runtime/Error注入 | 失敗を成功にしない、未知identity維持、全取得資源close、bufferzero |
| RBCR005 | short/zero/overflow/位置不進行/サイズ変化、不正UTF8/NUL/内部LF/0/65537byte | SS独立境界値から拒否、秘密を診断へ出さない |
| RBCR006 | file/root inode変化、前後割込/UID変化 | 前後snapshot不一致・割込・root脱落で非成功 |
| RBCR007 | 複数threadによる同borrowed owner読取 | 各読取に独立password owner、返却byte不共有。fixture計測同期とProduction同期を区別 |
| RBCR008 | native portでpublic file読取、非root拒否 | port正常IO値をliteral照合。native root/readonly admission positiveではない |

fixtureは実FD/IO＋明示したsynthetic root/tmpfs/readonly属性。Production expected生成禁止。root systemd実配置positiveは別隔離VM接続で確認する。coverage要求line/method/class/branch100%、例外/null/境界/並行を安易除外しない。実行command/commit/結果/XML/hash/coverage/BUGは146とmanifestへ後記し、未実行・限定成功を全PGPT認定へ算入しない。
