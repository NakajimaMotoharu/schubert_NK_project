# Readiness stream3 取得前保護

NK-OPS-001、RD OPS009/AVL/SEC・UI251・SS333/342343354/SSC308、BUG1414/YKT1178、実装判断PG-D425。group1228 P01807、開始.4/1.2/3共有pp固定。Caddy1＋Service2の原3site。Caddyはnullable InputStreamの旧body無し契約を、取得前の局所no-opとraw非null返却で保持し、全port/Scope初期化をgetter前にする。共通null拒否/Role/TLS/URL/status/500・1000ms/30分親/既Unit期限/read limit/disconnect/UNKNOWNを緩和しない。

新独立6（既MorningCaddyReadinessTestへ追加）：PT-CADDYSTREAM001非null同一stream一度close/read0、002null getterを許容し実stream無し/一回呼出/局所状態、003getter IO/Runtime/Error元identity、004close IO固定UNAVAILABLE/既MISSING・unknown元identity/一度close、005null port取得前拒否、006二独立stream/barrier並行・各close一度/状態共有0。期待は固定counter・literal Reason/message/identity、production helperからexpected生成0。Service既NativeTestの実loopback/NOFOLLOW/byte境界、既readinessの固定manager/kernel/HTTP vectorsも当sourceで再検証。

新source commit固定→pg5314_readiness_stream_selected.py green --group factory（予定1068実行129suite、既repeat10は一論理methodとして別記）→pg5316 actual3原site/取得前全port/Caddy null分岐の実stream成功後無call-new・全764物理差分→pg5318公開→pg5320原237分類。旧1038合算0、新whole予定3857/559/1661は未実行。1088へ当source/実日時・OS/JDK/tool/command/exit/TestID/class/method/fixture/独立期待/実際/XML/四coverage/static/hash・BUG/SSCをallowlist保存、raw秘密0。六format先行/NullAway・ErrorProne/三compiled static0/FES/flaky/skipped/notrun0、未網羅/native/全体/451は別未完。元job先行照合・二重起動0、実VM/DB/Backup/Unit操作0、原本/鍵/stash7/Currentbaseline/native/成功失敗証跡保持。
