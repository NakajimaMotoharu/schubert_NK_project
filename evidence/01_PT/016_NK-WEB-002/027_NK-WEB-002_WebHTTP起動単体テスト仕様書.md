# NK-WEB-002 Web HTTP起動単体テスト仕様書

PG220、RD SYS-001/006・AUT-001・TST-001～005、UI222/226/252、SS311/313/314/342/352/362、QA-045/UIC-005/SSC-074。対象`WebHttpServer.start/close/port`。Tomcat11の実loopback HTTP、Production `WebMvcConfiguration`/LoginController/Thymeleaf、caller提供のProduction security Filter登録境界を対象にする。これは起動assemblyのみであり、後続のWebApplication本番credential/DB/JMS結線・実NK CHR-A01/L01を完了としない。

| Test ID | 目的・事前条件/fixture/入力・操作 | Productionとは独立の期待値 |
|---|---|---|
| PT-SCR-109 | 私有temp dir、port0、検査用Filterで実Tomcat起動。GET `/login`、GET未知、HEAD `/login` | 127.0.0.1へbindし、Login HTTP200/UTF-8/title `schubert NK - ログイン`、未知404、Filterが各REQUESTを一度通る。公開業務resourceはFilterを迂回しない |
| PT-SCR-110 | null Filter/path/factory/factory result、欠落/非directory/symlink runtime dir、port負値/65536、null追加config、起動時bean例外、loopback設定拒否 | 全てfail-fast、listen/socket作成なし。起動失敗後はdestroy。秘密値を例外へ含めない |
| PT-SCR-111 | 起動後close、二重close、port読取、起動前後のHTTP接続 | 起動中だけport有効、close後connector終了。caller Filterのdestroyはcontainer所有。二重closeは追加副作用なし |
| PT-SCR-112 | 起動後にContextがSTARTEDでない場合、start失敗後のdestroyも失敗する場合をtest factoryで再現 | 前者はLifecycleException、後者は元のstart例外を保持しcleanup例外をsuppressedへ残す。失敗を成功に変換しない |

期待DOM/HTTPは上位UI/SSのリテラルから作り、Production controllerのreturn値をexpected生成へ使わない。環境・command・source commit・全Java coverage/静的解析、結果、関連BUG/SSC、sanitized XML/manifest/hashは後続正式runに記録。実Server保護Filter全機能・Caddy経路・実NK比較は別PT/CHR。
