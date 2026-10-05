# Web停止・UNKNOWN・context再試験結果

PG472-v6 actual0 / 69PT / 13suite / F/E/S=0、静的5module 0、NullAway/Werror/format PASS。実行開始 2026-10-06T06:52:00,697851122+09:00、終了 2026-10-06T06:53:05,044911779+09:00。base 3ec1d288746c2ecbcc5e38a48bdc81f5c3428247 + 未commit PG-D377変更群（正式source固定前）。

354の部分所有/request独立4PT及びHEALTH001..004のliteral全10拒否・全正常・短絡順序・例外identityを確認。WebRuntimeHealthのline/method/class/branchは実report全miss0。ただしgroup reportはcleanなし・旧execも存在するため全体coverage合格へ加算しない。当classは新規で4PTにより全条件を実行し、旧nativeにも存在しない。STOP001..005は元30秒・phase再試行・UNKNOWN後段保持・fatal identityを独立確認、UNKNOWN001は実retainUnknown interrupt保持を隔離JVMで確認。CONSIST003のv4/v5 Proto欠落失敗はBUG759/YKT539に残し、v6正規httpsでcontext保存故障を再試験した。PG471/native8結果を新source正式認定へ流用しない。

v1 actual1(API selector欠落)・Web追加not-runを維持。BUG758/YKT538を起票後、API明示選択v2は57PT10suite/FES0/static5zero、v3も各module非零・全指定class/fresh XMLを確認。0件guardは緩めていない。

環境 JDK25.0.4/Maven3.9.12/JaCoCo0.8.15/Linux。command `bash tools/quality/vm/050_s1/pg472_web_health_selected_v3.sh`。safe manifest `evidence/provisional/PG472-web-health-selected-v6/manifest.json` SHA256 0042c2b726fefe9b1ccd5369f7b6b9e4169085dbc3ddd7325aef6d76d20ab038。private log/source/XML hashesをmanifestへ保存しraw credential/session/token/keyは出力0。

次は変更群source固定→fresh全6→同source接続/native及び残counter。正式PT-WEB-20260925-24/1964PT53scope/48.3%は据置。未実行/中断/別source/ITST合格宣言0。
