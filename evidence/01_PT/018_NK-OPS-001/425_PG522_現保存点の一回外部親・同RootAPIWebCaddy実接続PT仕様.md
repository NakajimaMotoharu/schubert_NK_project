# PG522 現保存点の一回外部親・同Root API/Web/Caddy

## 限定実績（2026-10-08 04:57JST）

observer3payload new-only stage actual0/logf162b575…、一回外部startclient0、親INV8f4514e…/PID320189/ticks1508984/Job26968を捕捉。元1800sの当親継続、observer1954/A01待機18540へ再付着、二重起動0。今回Cleanup INV4e71…・Expiry INVcb737…はCode1/status0/Resultsuccess、Artemis INV3808…/PID353417稼働を観測。API/Web/Caddyと親DONEは未受入。
追加source51baeff97のreadonly pre-UI全列照合actual0、旧452行/その他23tableの全列保持、新10段の承認済みSKIPを独立literalで確認。Root私有snapshot60d4fcc3…・hostlog02782455…、safe evidence/provisional/PG522-preui-rows-v1/manifest.json。生存中の原本/Unit終端・親合格を推論せず、次current世代へ追随する。追加依存inventory22assert/166af4a8eでBUG822/YKT591工具範囲閉鎖、ProductionPT加点0。

NK-OPS-001、WBS-N05～N09、RD SYS/ENV/PER/AVL/OPS/MON、UI211212/231/243/251253、SS341342343/SSC193196198202212、QA047/QA045、BUG813814822・YKT582583585591。Productiona2/PG495/f699/schema028固定。旧PG505 timeout143/旧UNKNOWNを成功へ転用しない。

| Test ID | 独立期待値・前提／操作 | 合格条件・証跡 |
|---|---|---|
| PT-OPS-PG522-001 | PG521after f72d6c82…/complete479f6c1d…六key、全24table/452行、INVALID3/native15/全10Unit18終端、署名source/manifest/runtime3992c3bc…を二読。holdings/DBpeer/advisory0。 | current全原値/設定/unitFiles不変、旧cold/442/空startupを流用しない。新only observer3payload Root400/固定hash、start0。 |
| 002 | observerを開始し、一回予約を永続private guardへfsyncした後だけMorning --no-block startを一回。same-run/cutoff、元1800s。 | client0は親0ではない。guard後は再発行禁止、現在INV/PID/ticksへ再付着。Root/native元byte保全、旧/runを復元しない。 |
| 003 | 捕捉Root世代からordinary API UID/GID/groups/caps/NoNewPrivs/socket/readiness200-UP/info(source/schema/protocol)を二読。 | 同Morning/同Rootordinary/同ownedsocket、API所有を保持してWeb assembly→同ready→Caddy同世代zeroCaps/publicCA TLS/login200、元親期限renew0。 |
| 004 | CAtyped9にatimeだけ差、9field各変異、PID/INV/ticks/race差、予約-before-start順を独立fixtureで検証。 | host operator35assert＋stableActor20assert＋identity4test、syntax0。工具限定でProductionPT加点0。YKT585のatime誤分類を再発させない。 |
| 005 | 新親終端、同run全段/原本/intent退役/正常scope、owned逆順停止と資源後条件を後続独立照合。 | 元30分内真正DONEのみ受入候補、timeout/UNKNOWN/未実行は不合格保持。A01はTLS真正証拠後だけsharedCurrentdriver、DIF/QA045以外差分0。native100/正式同source品質は別matrixで全閉鎖。 |

作業群N05～N09着手前見積り低3/標準10.5/高26pp（leaf0.5+0.5+0.5+0.5+1／1.5+2+2+2+3／4+5+5+5+7）。N14やN15の費用、Production製造P/共通K01を重複加算しない。共有枠/PMO費未分離は実個別費null、実token取得不能N/Tnull。残90.9/269.8/642.6未較正。

順序command: `python3 -B tools/quality/vm/050_s1/pg522_prepare_observer_v1.py` → `bash tools/quality/vm/050_s1/pg522_parent_observer_v1.sh`（再付着）→ `bash tools/quality/vm/050_s1/pg522_a01_native_v1.sh`（TLS待機）→ `python3 -B tools/quality/vm/050_s1/pg522_external_resume_once.py` 一回。現記述時点ではすべて未実行。failure時は現在owner/source/保全物を保存して原因分類、二重startや雑停止0。
