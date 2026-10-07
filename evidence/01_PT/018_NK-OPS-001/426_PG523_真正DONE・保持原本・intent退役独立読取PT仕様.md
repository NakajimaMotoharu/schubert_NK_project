# PG523 真正DONE・保持原本・intent退役の独立読取

NK-OPS-001、WBS-N09/SS341342343353/SSC198212/QA047。Productiona2/PG495/f699/schema028固定、既N05～N09群3/10.5/26pp内、追加群予算を二重加算0。正式run24/1964/53scopeは変更しない。

- PT-OPS-PG523-001: 今回親bootcc9/INV8f4514e…/元Main320189/start15089848500us/Job26968を独立固定。PID1 start19:46:29.837227UTC、success/DONE20:08:51.344734UTC/monotonic16431357068usの4record、elapsed1341.508568s<=元1800s。GC後の空INV/0codeを成功根拠にしない。異boot/異INV/非PID1/UID/COMM/Unit・過去Job/stop/failed/欠落/重複/範囲外は拒否。
- 002: 新M-A/署名187/StartupRoot FD/RO親DB(appPG523-completed-readback/advisory71419602)/十Refを保持。Current epoch ISSUED、boot/run91a/cutoff2026-10-06T12:06:14.564793Z/activation179758…を固定し、既MaintenanceRunFilesのwhole-graph readbackが当SUCCESS doneを返すこと、endedAtが今回start～PID1done内であることを二読。新規done書込/旧143正常化0。全`.start.intent` suffix不存在を要求し、単にliteralAPI.start.intentだけを探す誤判定をしない。3request空、API/Web/Caddyは捕捉した現在同世代liveのまま、起動/停止0。
- 003: DBの旧452行全列を固定PG521afterから保持、新10段はSS341同日成功再用のSKIPPED/zero/ALREADY_SUCCESSFUL/literal理由・同businessdate2026-10-06・各step前最大attempt+1・開始終了有効時刻。古い別cutoff SUCCESSを今回新SUCCESSと読み替えない。A01後の正規Web/session/log変化を「他23table不変」へ偽装しない（pre-UI全列保持は別PG522証拠）。
- 004: Python独立80assert＋JavaCLI6assert/nullNPE0/所有actions0、正規/欠落/空/未知/型/bool/row変更/重複/branch/currentframeとPID1 negativeを完走。undefined0、javacWerror0。firstcompile-v1は未実装fixtureのrepository import漏れで拒否（VM0）、元source `.java.failed-v1`/log保存。是正compile-v2はactual0、host-only source/staticをguestへ移さない。工具試験をProduction PT/coverageへ加算0。
- 005: DBrollback/close→snapshotownBackend0→全batch/原本/startup/full18保持→十Ref逆順Unref/bus/全FD/A/M正常後だけ新completeを公開。close UNKNOWNはretainし、旧scopeのcloseを補完しない。実API/Web/Caddy逆順ownedTERM/native100/正式は後続で別受入。

実行前source固定commit/push後だけ `python3 -B tools/quality/vm/050_s1/pg523_completed_native_v1.py` を別new-only tools-v1/SAVE-v1へ一回。classはhostcompile-v2の2runtimeclassだけ、immutableRoot400/hash、guestにsource/Pyflakes追加0。現記述時点でVM未実行。actual/日時/OS-JDK/source/hash/全新scope・peer0後条件は結果追記する。
