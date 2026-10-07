# PG504 同inode明示mode・一回resume再試験仕様（実行前）

追加評価BUG813：当runtime/全新scope正常・既原値保持は実測通りだが、PG502のnative role完全性は不足。PG504 normal receiptだけで後続native採取の全前提合格を認定しない。SSC193/196の6role cross-checkと正常owned停止後の別準備を要する。

現在結果2026-10-08 01:34JST：hostJava10/Python65/Werror0、初回preflightのID負チェック失敗は不合格保持（BUG812）、new preflight-v2独立25正常。native88050 actual0/5.969021s・101..103全新scope正常。Root after SHA67fa28ad6f289589994af0be7022a20fe12b673685d0c151ffb791dd91fec52e・complete SHAac7a0eb9af359638ed84bab5951afe69cfc2636e2b460233f82029560aa762ad、safe evidence/provisional/PG504-runtime-normal-v1/manifest.json。以下初期「未実行」欄は計画履歴で、現在結果はここを正とする。親全体/coverage100/全faultmatrix/正式は未受入。

NK-OPS-001/NK-BAT-001、WBS-N14/N11/G13.07、RD SYS-011/OPS-009～017、UI251～253、SS341343353/SSC198202206208、QA047/BUG811812/YKT580581。sourcea2/PG495/schema028/bootcc9不変更。
PG503原実source/log/143/closeUNKNOWN保全。限定handoff actual0/complete SHA1c69227dfba0df61f3f546307ff5055d09cfbf655cc73360ae3ef23421732fec後、当固定空runtime Root0700/inode2576/原9metadataだけを新所有下に0755へ明示fchmod/dirsync。期待0755を緩和しない。

| Test ID | 観点/fixture/操作 | 独立期待値・根拠 | 初期状態 |
|---|---|---|---|
| PT-OPS-PG504-001..075 | Java10/Python65の固定引数/ASCII resume・有効全config/raw不変/Rootowner/ACL/foreign/null | 411独立SS goldenを別tool sourceで再試験、別既成功/Production expected生成0 | 未実行 |
| PT-OPS-PG504-076..100 | 全9原metadata変異/欠落/null/foreign/ACL拒否、実umask077→700→heldFDchmod755/同inode/UID/GID/empty/ACLなし、driver ID/path/exit join | 独立literal metadata、真host kernel fixture（私有新tmpだけ）。mode0755必須・一般umask緩和0・VM操作0 | 未実行 |
| PT-OPS-PG504-101 | 新M/A/専用DB/advisory/十Ref・現署名/全10cold/full24-442/102＋startup/native保持 | PG502after/complete・PG503handoff receiptの固定hash、全raw independent二読・他owner0 | 未実行 |
| PT-OPS-PG504-102 | 当空runtime同inode限定mode修正→fixedNAME new-only/一回reload | 0755/ACLなしで固定二引数、一件のeffective宣言だけ変化。他全security/元期限/原値不変、start/DB書込0 | 未実行 |
| PT-OPS-PG504-103 | DBrollbackclose→十Ref逆順/正常bus→A/M正常 | 全新scope正常後だけ次external durable予約。旧UNKNOWN/143を正常化しない | 未実行 |

commands: bash tools/quality/vm/050_s1/pg504_resume_compile_v1.sh; python3 -B tools/quality/vm/050_s1/pg504_resume_native_v1.py（新stage/SAVE/当同inodeの認証後一回）。stdoutのIDはPG504-resume-native-v1に一意対応、旧PG503誤labelはmanifestで元label/実command/正規IDを対応。全fault/競合/native100/親DONE/正式は当正常だけで加点0。生原値/credential/tokenはGit禁止、結果command/exit/source/date/hashはsanitized manifestへ記録。
