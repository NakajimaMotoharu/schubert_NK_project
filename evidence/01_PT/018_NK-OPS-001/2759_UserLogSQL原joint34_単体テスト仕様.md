# User/Log SQL界面・原joint34仕様

2026-10-30、主P010-01/関連P010-04/P018-09追加0、着手前1/4/8pp、source6b53/normal14216。元NK-ADM077/079仕様を現在の原各9methodへ適用し、SQL009各full pageを追加記載する。RD FUN008/009/AUT002003/DAT003/MON、UI225/235/236/241、SS312/323§9.4/9.5/331/332/411/451。

全Test UserSQL459/LogSQL507行とproxy/helper/initializer、Main repository283/216、Request/認可/RequiredColumn/固定例外/必要protocol型を全body確認。元Core4/Response4/LogPlain8も既全body確認済みの原wholeをそのまま選択。新SQL18＋必要な既Plain16を一fresh JVM/一exec/5suite/34methodで実行する。旧request proofはquery methodが未達であり、そのmethodだけの別execと合成せず、全Sourceを同一execで測るための必要な16関連回帰。既16を新unique数へ再加算しない。

SQL001～008の独立表は元077/079を継承：手組wire offset、固定typed tuple、手算50/100page、materialized one count/page SQL文字列とbind順、literal wildcard quoting、UTC micro→millis、ADMIN/null境界、RS→PS解放、borrowed connectionを変更/commit/closeしないこと。SQL009はUser id1～50の50行/Log id100～1の100行を固定loopで手組し、page999999はbindのまま・応答1/full page・順序/件数を独立期待。LogSQL004の2088byte goldenはUI offsetから固定literalで組み、production codecからexpectedを生成しない。

fixtureはJDKのpublic JDBC三interface自己Proxyだけ。Driver/URL/DB/ネットワーク/私有reflection/鍵/HMAC/JCE/Root/VM/permit/intentは呼ばない。未知methodはAssertionError、SQL/invalid tuple/close failure/例外graphの故障注入なし。null/USER/不正page等の期待拒否はSQL try-catchの前で止まる。borrowed正常tuple/normalcloseだけで、SQL catch/preserveFatal/Graph9/crypto/response snapshotはHOLD。postで元exec中の所定禁止四Product probeが0であることを確認し、不明/非0は合格へ読み替えない。既sourceの成功は再利用せず、実DB SQL構文/plan/lock/DB後条件は未検証のまま。

全四Source/四physical=UserQueryRequest/LogRequest/UserQueryRepository/LogQueryRepository。Request二Sourceは旧未達proofを履歴保全した同一exec新資格候補、Repository二Sourceは正常界面だけでerror枝未達を保持。四counterを測定し、未達を除外/無意味assertion/合成で隠さない。新Test IDは作らず元18IDを当sourceへ再資格する。

command `PYTHONPATH=tools/quality python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg14742_user_log_sql_joint_thirty_four_pt.py`、後続14744専用SQL-interface post。全normal input/六Jar/static14224/元環境/全Test path-hash、eligible text補助六反例を確認（語検査を許可根拠にしない）。XML F/E/S/not-run0、一exec/session/CRC/全closure/禁止probe0/独立期待・byte・ownerを照合。manifestに日時/OS-JDK/tool/branch/source/commit/command/exit/入力期待case/実XML/exec/coverage/hash、結果2760。正式1964-53/歴史17-190/工数null/QA051final/全安全HOLD不変。
