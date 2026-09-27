# 実リリースmanifest hash PT仕様書（PG300、未認定）

Program NK-OPS-001、Bootstrap.StartupReleaseManifest.create/sha256/selected/manifest/checked/version/NioIo/Snapshot、FixedServiceIdentity.configurationGroup。RD SYS-002/004・OPS009、UI212・251、SS311/342/343 SSC089、D04/05。親A保持中に使用する非秘密read-only adapter。唯一current symlink以外はNOFOLLOW、全所有close後だけ実byte hashを返す。BOM全artifact/root/current permit認証は別必須で未実装。

| Test ID PT-OPS-RELEASE | fixture・入力/操作・独立期待値/根拠 |
|---|---|
| 001 | 実Linux保持FD＋権限模擬port、root755/app・releases・version750、regular640/単一link、public abc。独立既知SHA256 `ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad`、全owner0、内容不変更 |
| 002 | absolute固定releases直下、version1/64、相対/root/他parent/`.`/`..`/65/非ASCII/先頭dot拒否。current非link/相対target/target directory・manifest symlink拒否 |
| 003 | 全typed metadataの欠落/未知型、UID/GID/mode/link/dev/ino/size境界、ACL非空、0/1048577byte拒否。期待値はSS343のliteral権限・型・上限 |
| 004 | 全before/after/再open観測点で独立ino変更、mtime/ctime変更、selector変更を拒否。opt/release parent namespaceも再保持し一致確認 |
| 005 | 0read/短EOF/過大stream/前後size違い/attributes-selector-read-open-close IO fault。上限1048576 zero byteの独立既知SHA `30e14955ebf1352266dc2ff8067e68104607e750abb9d3b36582b8af909fcb58` |
| 006 | 各directory/entryの取得・close位置故障、全owner one-close/0残留、未知例外identityを正常IOへ変換しない |
| 007 | null constructor/selector、相対・非正規root/不正GID、unsigned dev/ino/GID最大、16並行独立fixture |
| 008 | native factory/read/stat/link syscallを実行し、開発hostのProduction配置不成立を起動認定へ算入しない |

NSS追加観点は既存PT-OPS-SERVICEID001内で固定`getent group schubert`だけの独立986 goldenと不正GID拒否。sorted service groupsから設定groupを推定しない。Native018/019では隔離VMのroot-owned唯一currentと実abc/権限/ACLを、実API/Web UID＋private mountから同readerで確認。abcは故意に有効BOMではなく、fullgate=falseを必ず保持する。

実行command/日時/OS/JDK25.0.4/Maven3.9.12/対象source hash/coverage/static/初期非成功・BUG/SSCは120と`evidence/provisional/PG300-301/manifest.json`。期待hashはProduction methodから生成しない。初回未実装RED、compile/null静的/fixture mode調整は成功に算入しない。skip/failed/not-runなしの実行だけ限定結果へ記録、正式全scope/CHRは別。
