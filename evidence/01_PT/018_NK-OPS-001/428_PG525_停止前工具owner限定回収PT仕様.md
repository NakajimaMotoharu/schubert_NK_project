# PG525 停止前工具owner限定回収（SSC213／BUG823・YKT592）

Production source a2e98ce9e96c42425921e3686e8ae7a94bff9e6c、PG495/schema028。設計SS343/353 SSC213、設計only PR48 main19f15e4aeb8e1f667f6ab33a09a4f4922c9355f9。業務仕様・Current baseline・外部表示順の変更なし。

| Test ID | 独立期待値・目的 | 証跡 |
|---|---|---|
| PG525-H01 | 固定owner PID560210/ticks1926229、Ref560239/ticks1926340、Root UID四値、全task子、argv SHAを照合。欠落/null/bool/foreign/誤世代38assert | pg525_prestop_handoff_test.py stdout |
| PG525-H02 | PG502 cold-lock五key/owner3項/lock9値のliteral正常・欠落/null/bool/誤mode/inode/別artifact73assert。当前工具の関数を直接試験 | pg525_reference_schema_test.py stdout |
| PG525-V01 | 全10Unit18値、live API/Web/Caddy/BrokerのPID/INV/ticks/cgroup、全24表462batch行、設定、startup、原本、Backup、native、固定runtime、release署名/readonlyを前後二読で不変。PG524 raw SHA15fa5248…とSQLの元JSON順を保持 | Root pg525-prestop-owned-handoff-v1/before.private.json、complete.private.json |
| PG525-V02 | M/A inode/FD/FLOCK、当工具batch peer・advisory（0/0又は当一件だけ）、immutable6payload、Ref→Java一回pidfdTERM、全owner消失・自peer/lock0。業務4世代はlive維持、stop/start/reload/revoke/DBwrite0 | 同term-reservation/peer-before/complete（私有） |

実行: `python3 -B tools/quality/vm/050_s1/pg525_prestop_handoff_native_v1.py`。SSH/stdout/logはRoot/host私有へ保存、GitにはSHA・終了値・集計のみ。new-only予約の再実行は禁止。終了前preflightは同source execute(False)で読み取りだけ行う。旧PG524 actual143になってもclose UNKNOWNは正常化しない。

静的: Python undefined0（固定AST注入名だけ）、独立111assert。工具試験はProduction PT/coverageへ加算しない。Production全回帰/native100・正式認定は未更新。VM結果は実行後追記する。

実結果: source886551e32、native3925 actual0/log997c0de4…、Root before65d6da45…/completeee4317dc…。Ref→Java限定TERM/全owner消失・自peer/FLOCK0/全raw前後二読/live4保持/業務操作0を独立再読。旧native96236はactual143/947.317479852s/log1a8d0997…・closeUNKNOWN維持。safe=evidence/provisional/PG525-prestop-owned-handoff-v1/manifest.json。PG526fresh再試験と横展開閉鎖は未完。
