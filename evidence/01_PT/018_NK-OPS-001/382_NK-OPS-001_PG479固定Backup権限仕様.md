# PG479 固定Backup入力権限単体仕様

Program NK-OPS-001 / MorningBackupArtifacts.withInputs,inputMode、RD OPS009/UI251/SS341 SSC121・SS343§6.9/SSC197、BUG771/YKT551。

| Test ID | 入力・操作 | 独立期待値・根拠 |
|---|---|---|
| BMODE197001 | config固定8名、credential=false | 手書きliteral表でAPI/Web envだけ0100600、静的Inspector env含む他6名0100640。SS343§6.9。Production catalogからexpected生成0 |
| BMODE197002 | 手書きcredential17名、true | 全0100600。Root:Root秘密入力契約維持 |
| BMODE197003 | null/空/未知/相対path/runtime env/他catalog取り違え | null契約違反・他IllegalArgumentException、未知名を既nameとして許可しない |
| BMODE197004 | VM hostview実8file/全24table/全old tree、read-only capture | actualInspector0640/旧suffixだけ0600の不一致一件。旧全411DB及び他23table原値一致、原本/Backup旧全filebyte・inode属性保持、new2RUNNINGは未完了 |

fixtureは名前/modeを仕様から固定。API境界nullをcatchして正常扱いしない。並行/再送は既Root/M/A/held inode/current署名・親元30min契約を維持し、既runningを修正bytesで継続したとは扱わない。DDL/crypto/画面変更0。実archive/nativeの正常完了は別必須で、policy testだけでBUG/YKT全完了にしない。

Command: `bash tools/quality/vm/050_s1/pg479_backup_mode_selected_v1.sh red` / `green`、新log v2。VM readonly: `python3 -B tools/quality/vm/050_s1/pg479_capture_host.py before-terminal` / `after-terminal`（各一回、Root400固定工具・new0600私有snapshot）。JDK25.0.4/Maven3.9.12/JaCoCo0.8.15/SpotBugs4.10.4.0、source318c＋保存diff→固定commit後fresh全6。Coverageは新policy method/line/branch100必須、class/global/native100は別未達を明示。
