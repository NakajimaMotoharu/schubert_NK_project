# Web Outbox借用読取の型付き解放

SSC-469、BUG-3290、YKT-2597、SS332/351/354、UI252、P004-05／F03。4682/4683と2665の元26件を保持する。原SQL、固定querytimeout、三列、UTC照合、六系列、失敗と非公開条件、借用Connection非変更を元独立期待で検証する。

WEBOBXDB011を追加。元11の所有判定のうち、合成SQLExceptionをgetLongと行closeへ同じオブジェクトとして渡す。固定期待はJDK self-suppression規則によるIllegalArgumentException、そのcauseは同じ合成SQLException、stmt closeは1、rows→statementの順、Connectionのclose／変更なし、成功Observation公開なし。実リソース・外からの例外文字列は使わない。

元27の通常一runと固定source、Checkstyle/PMD/NullAway/SpotBugs、公開descriptor、実class/CRC/JUnit/exit、同単一execの生と既定の四counterを確認する。型付き解放によりJDBC例外の外部優先と既条件を変えない。全451、実DB、後続受入は継続する。
