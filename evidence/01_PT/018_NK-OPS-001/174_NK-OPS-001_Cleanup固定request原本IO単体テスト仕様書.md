# 174 NK-OPS-001 Cleanup固定request原本IO単体テスト仕様書

Program ID NK-OPS-001/NK-BAT-001。Production `CleanupWorkerRequestFiles` constructor/`prepare`/`read`/`retire`と内部directory/file/write/read/verify/guardを対象。RD OPS-009/BAK-001、UI251、SS341§2/3/7・342§4・343§6（SSC104/PG325）、Test ID PT-OPS-CREQFILE001～008。root親が与える固定`/run/schubert-nk/cleanup-request`相当の借用root内で、原本file `cleanup-request`だけをnew-only公開・読取・限定退役する部品。実path選択、M/A・DB・backup・削除許可はcaller責務で別gate。

前提/fixture：Java25.0.4/Maven3.9.12、既存`BackupPublicationFixture`の合成private root/metadata/IO fault portを転用。固定expectedはSS104の独立ASCII literal `NKCLEAN1`/run・activation各UUID/cutoff UTC µs/manifest小文字64hexであり、Production `encode`から期待値を生成しない。合成rootでroot UID0、0700 directory/0600 file/tmpfs/ACL空、7byte分割IO等を注入する。実Linux root/systemd配布合格とは区別する。

| Test ID | 入力・操作 | 独立期待・後条件 |
|---|---|---|
| CREQFILE001 | 固定requestをnew-only publish→literal file read→readback→retire | ASCII全byte/値一致、part消滅、限定原本だけ消滅、借用owner全解放 |
| CREQFILE002 | constructor/prepare/retire null、非root、owner/mode/ACL/RO/FS/map不正 | null境界はNPE、他は固定拒否、既存file不変更。NPEをcatchして正常扱いしない |
| CREQFILE003 | missing/他名、同名・既存part collision | read/retire失敗、公開原本/既存part/他file不変、fallback/修復なし |
| CREQFILE004 | prepare/read/retire全IO位置、write/read進捗0/負/超過、size/EOF/nullable resource | 不確定を成功にしない。全所有channel close、原因値非公開 |
| CREQFILE005 | request byte改変、退役期待値不一致、file dev/ino/size/mtime競合 | canonical/原本照合失敗、限定対象を消さず、既存値を採用しない |
| CREQFILE006 | unknown Runtime/ErrorとIO/close複合、割込 | 未知identity保持、既知診断固定、割込flag保持、所有者解放 |
| CREQFILE007 | 独立root16件を4 threadで並行publish/read/retire | 各scope独立、他requestのfileを変更しない。並行実施だけで親M/A保証はしない |
| CREQFILE008 | retire後sync不確定、read中同名inode交換 | 逆操作/再作成/修復せず非成功、残存original/retainedを保全 |

Run command、OS/JDK/tool、branch/commit、F/E/S、JaCoCo line/method/class/branch、静的解析、source/XML hash、関連SSC/BUGを175と`evidence/provisional/PG325-cleanup-request-files/manifest.json`へ保存する。Coverageは新class4指標100%を限定累積で確認し、正式全scopeと混同しない。実固定path/source/LoadCredential、親排他と子受信、原本run照合、cleanup実行/再送は未実行。全PT期待はliteral・fault注入・file後条件から独立算出する。
