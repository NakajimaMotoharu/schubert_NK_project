# Backup失敗行の時刻瞬間照合の単体仕様

NK-BAT-001／NK-DAT-001、BAK-001／OPS-009、UI251、SS331／SS332 SSC-056／SS341／SS343、BUG-3754、YKT-2933。対象は `BackupFailureSnapshot.verifyLatest/verifyRow` の JDBC 4.2 読取時刻二列。合成ポートのみ。

| Test ID | 合成入力・独立期待値 |
|---|---|
| PT-BAT-BACKUP-UTC001 | UTC基準の開始 02:00:00.123456 と終了 02:00:03.654321 を、明示した+09:00の11:00:00.123456と前日-05:00の21:00:03.654321で返す。いずれも同じ瞬間。両Backup行と最終ID再確認を通過し、各取得行を各文より先に閉じる |
| PT-BAT-BACKUP-UTC002 | 開始の壁時計を同じにして+09:00へずらす場合、終了を1µsずらす場合の二つ。両方を拒否し、固定IOException、原因・抑制なし、取得済み行と文を逆順で一回終了 |
| PT-BAT-BACKUP-UTC003 | started_at／ended_atを一つずつnull。固定IOExceptionと同じ既取得資源の逆順解放。二行目や最終再確認へ進まない |

期待値はSS332の物理値変換規則と、上表の固定時刻から判定する。借用Connectionのcommit、rollback、close、実DB、既存データや実Backupに触れない。修正前の再現と現単一exec、既存PT-BAT-SSC461-BF001～004の最小回帰を独立に識別する。
