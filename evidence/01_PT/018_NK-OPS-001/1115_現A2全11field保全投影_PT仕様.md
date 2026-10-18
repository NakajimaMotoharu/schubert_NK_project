# 現A2全11field保全投影 PT仕様

NK-OPS-001/OPS009/UI251/SS343354、Test OPS-FRESH-VIEW-001。1114の真正5434/現A2/BOM78/native88が前提。独立期待値は固定原snapshot SHA `4ab25ad070358ef6580a29855c2cbd1fe00f9cb32f6a514bc279a932bcd0ba94` と原11field名。production処理でexpectedを生成せず、原DB/Backup/native等を省略せず完全に取り出す。

`PYTHONPATH=/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime python3 -B tools/quality/pg5436_current_full11_view.py` を新専用一回。root600/単link/NOFOLLOWで元保存snapshot hash・source/BOMを確認し、全11field/24表/10Unit/88exec/PID0Job空を確認、currentlink/boot不変とactive/startintent無しを読取、新専用beforeへprivate保存・fsyncする。元snapshot読取時点は5434であり新DB照合と称さない。start/stop/reload/DB更新/旧permit復元0、通常ログへDB値/credential/鍵/raw nativeを出さない。

工具管理一は固定hash、11field、88exec、snapshot元時刻の明示とsubprocess無し/static0を確認する。異常は非0で保存しstage/placeへ進めない。結果は1116、実before hash/source/元snapshot hash/exitを次候補roleへ固定する。1263同群0.5/2/6固定・別予算加算0、正式1964/53/QA051final・工数nullを維持。
