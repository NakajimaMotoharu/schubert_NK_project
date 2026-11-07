# NK-WEB-001 Session SQL store全port単体結果

015088/PT-WEB-JDBCSTOREPORT001..015、Test/source d87efbe02857b397d6af100d61ede8a77dcf69ce、Main7aed8eace7c844c2f79f2e39db766faf914890d5、Verifier30f0202a54ccbaf717d2c0e9947db07c3068862d。PG22360 lint/Werror0、22362 rawPMD11は一件ずつ非該当根拠を記録・適用0/CS0/processing0。Main22084/六静的22086を同byteだけ再利用。PG22350全15成功/F/E/S/abort0/真正終了0、一回実行のみ。22366受動metadata0、22370標準生成constructor metadata0、22368独立post0、再実行0。

対象全Codeはinstruction511/line123/method13/class1/branch30、全未達0。physicalは本体とprivate InvalidStoredRowの二class、markerの生成private noarg constructorだけ標準JaCoCo0.8.15 filterでCode分母零/N-A、raw1/1への到達は残す。独自除外なし。本体CRC15f3bcdbf41381d4/raw160/172、marker125a9ee56a055ad6/raw1/1。標準TWR filter前のraw172/172を主張しない。一exec/PG22350-JDBC-SESSION-STORE15一session、別source・旧execとの合算なし。

独立固定五SQL、九columnの型/getter/UTC/bind位置、insert9/CAS10/delete二種、version0..999999999/idle1..28800/key1..16/ciphertext形式29..16436、null/各不正column/二row/cleanup失敗/finite cause-suppressed Error identity/全JDBC callback失敗/二worker各25回を確認。borrowed Connectionのcommit/rollback/close/setAutoCommit等は常に禁止assert。JDK JDBC interface ProxyはSQLを解釈・実行せず、owned Statement/ResultSetだけcallback順を確認する。fake closeの失敗時はclose試行を確認し実資源解放成功へしない。

実methodは本体とSessionStoreException・InvalidSessionRowException・SessionPayloadIdentity・WebSessionRow・EncryptedSessionPayloadの六Main、許可内のconstructor/不変条件/opaque copy/local fatal helperだけ。marker初期化も実測照合。record生成accessor等は標準filterでCode表に出ないが、手書aad/codec/lifecycle/暗号はhit0、四guarded型/driver/provider/Cipher/DB/Root/native/network初期化なし。支援五sourceのwhole加算0。公開固定UUID/hash/zero opaque bytesだけで実session/Cookie/token/鍵を保存しない。

BUG2427/YKT2172の工具path・正規CS exit count guard、BUG2428/YKT2173の五静的siteを原失敗22352/22358保持、同値是正d87efbe・最終静的22362・元15/独立postで有限範囲をCLOSEDとする。これはDB transaction/lock/constraint/grant/永続化/実認証/session filterの受入ではない。旧logging/JdbcWebSessionStoreTestのPostgreSQL BeforeAllは実行せずNOT_RUN/HOLDを維持。

command: `python3 -B evidence/01_PT/015_NK-WEB-001/input/039_jdbc_session_store_independent_post.py`。元command/実行日時/OS/JDK25.0.4/JUnit1.13.4/依存/source/input/XML/coverage/CRCとhashはmanifest.filesへ一意に記録。manifest `evidence/01_PT/015_NK-WEB-001/evidence/PG22368-jdbc-session-store-independent-post-v1/manifest.json` SHA256 `9c7aa208176af48724db565d5f60cb123d69deb2d90b329bb8362bc455398591`。unique415→430/whole93→94、正式1964PT/53scope/新leaf0/工数null、451全体/IT-ST未完を維持。
