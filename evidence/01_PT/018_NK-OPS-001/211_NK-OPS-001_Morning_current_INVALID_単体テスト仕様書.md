# 211 NK-OPS-001 Morning current INVALID・単体テスト仕様書

Program ID: NK-OPS-001。対象: `MorningCurrentInvalidation.invalidate`、`MorningControlScope.execute`。関連RD OPS-009、UI251、SS341§5/343§6.15、SSC-089/105、PG344。承認済み原本から新epochを作り、親がM・A・専用DB/advisory・原本を保持し、固定8 Unitの停止とA取得後のfresh終端を確認した後にだけ`epoch.current`をINVALIDへ変更する。permitのISSUED、backupやcleanupの成功、通常業務起動は本仕様の範囲外。

| Test ID | 事前条件・入力・操作 | 独立期待値・根拠 |
|---|---|---|
| PT-OPS-MINVALID001 | 手書きboot/epoch/run/activation固定UUID、未完了run、fake store | `root→write INVALID→readback→root`、同boot/epoch/activation・digest空の値だけ返す。SS343のcanonical原本bindから期待値を手書き作成 |
| PT-OPS-MINVALID002 | completionを持つrun | write/read0、非成功。既完了原本を新たな現在許可へ結び直さない |
| PT-OPS-MINVALID003 | root又はwriteがIOException | write前root拒否、又はwrite失敗後readback0、元例外同一。欠落を成功に変換しない |
| PT-OPS-MINVALID004 | write後のcurrentが別epoch | readback不一致を非成功。原本値を補正・復元しない |
| PT-OPS-MINVALID005 | epochがboot/run/activationと同一又はnull | write0で拒否。distinct新epochの内部不変条件 |
| PT-OPS-MINVALID006 | native factoryにCLEANUP actor又はnull入力 | 固定Morning actor以外はIO前拒否、nullは契約違反。native正経路は実VM別確認 |
| PT-OPS-MCTRL010 | 手書きevent/owner、未完了原本 | `M→original→stop8→A→fresh8→INVALID→trusted work`、INVALID時とwork時にM/A保持、closeはA→original→M |
| PT-OPS-MCTRL011 | INVALID writerがIOException、又はnull callback | 失敗後work0、A/M解放、元例外同一。null callbackは副作用前拒否 |

独立oracleは固定UUID、手書きevent列、fake Storeを使う。production methodで期待値を生成しない。`StartupPermitFilesTest`が固定byte、mode、atomic replace、force/sync/readback等を別途検証する。本testのfake store成功を実tmpfs原本・実A・実8 Unitの合格に読み替えない。既存VM保留run/旧currentへ書かない。正常・境界・異常・例外・null・所有順を上記で覆い、同一A下の並行は既存StartupPermitFiles/lock試験、再送はINVALID後の新epochと旧ISSUED拒否を同試験で別確認する。

実行command、OS/JDK/Maven、branch/source commit、line/method/class/branch coverage、結果・証跡path/hash、関連BUG/SSCは212/manifestへ記録する。coverage除外なし。native実8 Unit成功・Morning main・resume・backup/Cleanup/permit未接続による未被覆は合格に算入しない。
