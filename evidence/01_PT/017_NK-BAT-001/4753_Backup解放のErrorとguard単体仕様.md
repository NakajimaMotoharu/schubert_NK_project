# Backup失敗行のErrorとguardの単体仕様

NK-BAT-001／NK-DAT-001、BAK-001／OPS-009、UI251、SS332 SSC-481・SS341・SS343、BUG-3757／YKT-2935、WBS-P017-06・F03/2-2-b。

対象はBackupFailureSnapshot.verifyRow。条件分岐の数値で区別できないJava例外捕捉種別を、既存ローカルJDK代理オブジェクトと独立した期待順で確認する。

| Test ID | 合成入力・独立期待値 |
|---|---|
| PT-BAT-BACKUP-UTC011 | 行nextと行closeへ同じ合成Error、文closeへ別のSQL例外。元Errorを伝播し、文closeだけを抑制に保持。行と文を各一回、行→文で解放 |
| PT-BAT-BACKUP-UTC012 | 行を閉じた直後のguardから固定のchecked IOException、文closeから別SQL例外。元IOExceptionの同一性と文closeの抑制一件。両取得資源を行→文で解放 |

借用Connectionのclose、commit、rollbackは代理オブジェクトで拒否する。実DB、サービス、既存ファイル、認証情報を使わない。試験・製品の固定版、コマンド、終端、XML、四coverageと静的結果は実行manifestに記録する。
