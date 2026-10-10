# SSC245 cold同peer親子の事前照合・限定契約

NK-OPS-001 / SS343353 / SSC245 / QA047 / BUG1017～1018 / YKT786787。設計source040f5364d、PR83 main399bcedad。実装開始source d91a61c01。新scopeの正常受入はまだない、旧1037 actual UNKNOWN・正式24/1964/53は保持。

PT-DEP-1049001～008：親5463/1373880、子5489/1373951固定tuple。独立stateful fixtureの手書きcall sequenceで二pidfdの先行束縛、親予約後全tree再読、親一回signal/wait、孤児peer二読、子予約後再読/一回signal/wait、逆順両closeを検証。境界=null、bool、同PID/悪generation、callback欠落、tree/orphan変化、各open/reserve/send/wait/close例外、timeout。親不明なら子送信0、予約後失敗/close不明は成功0・observer保持、SIGKILL/再送/直接DBterminate無し。host8case PASS。最初のTDD harnessではcallback個数誤りで7case/E1、その未合格を保持・最終成功へ加算しない。

PT-DEP-1050001～003：実起動経路の固定世代/子PPID/Rootauthority/全task/FD metadata/kernelFLOCK/実parentDBheartbeat query/同socket inode、全24原値/十coldfull32/configを二読。これは副作用境界のAST・固定predicate guard3caseで、実VM証拠を代替しない。PG1050 preflight-v1 actualはhostTimeoutExpired120s/hostexit1、guest成功0、Ref/FD取得前のpeer行80で拒否。DB inet文字列にprefixが付くことを裸hostへ混同したBUG1018。新observer6897/1800493は全task子0・FD0/1/2全pipeの3個のみを現在照合し、本人pidfd普通TERM一回/終端だけを認定。hosttransportは既timeout済でguest exitはunknown、143/normalを推定しない。元5463/5489・DB/十Ref・全原値/業務start不変更。

修正はSQLの`host(client_addr)`でhost投影を明示、期待localIPv4/IPv6・client_portと本人socketinode・固定heartbeat/transaction generationは不変更。検索client_addr::text/host(client_addr)/clientAddressの実行工具該当は1050だけ、testはSQL独立guard。pg1050 future builderは修正するが保存v1 guest scriptを改変しない。PT-DEP-1051001～002で新slot/preflight-v2/全runlabelと開始source凍結・persistent logを検証し、v1へ再実行しない。

Command：各 `python3 -B -m unittest discover -s tools/quality/vm/050_s1 -p <pattern>`。1049=8、1050=3。1047拡張3/1023=6/1037=3もPASS。同sourceまとめ再実行とhash資格・実1051 normalclose/postは後記。Production coverage100の新認定や旧actual成功ではない。fullMavenを管理/工具変更だけで反復しない。

証跡W=`/home/mini/codex/project1/work/pgpt-runs/PG379`：pg1050-cold-tree-preflight-v1/guest-script.private.py不変更、v1 manifestはproducerがtimeoutで未作成（欠測を0としない）。別診断はtree_identity正常/peer line80 AssertionError。新実1051はbegin.safe/manifest.safe/persistent private log、新source/run/exit/whole metadata/privatebefore hashを照合する。私有原本/credential/heap/tokenをGitへ入れない。親子の実TERMはまだ未発行で、fixed once handoffは全事前資格後に別scopeで行う。
