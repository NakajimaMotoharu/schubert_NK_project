# DB接続二Source二十一method独立oracle対応 結果

仕様3849/scope641。Main7aed不変更。PG24122公開Source/metadata確認exit0、元23656十五＋23704十四の成功を再実行せず、21method/29case/70assertion snippetを現23972・Source別23982・SS342343へ対応。実moduleはbootstrapでありpackageのapiから推測しない。

|Source|method|元Test ID|独立期待の範囲|
|---|---|---|---|
|ServiceDatabaseAdmission|<init> (Ldev/codex/schubert/nk/storage/ServiceConfigFiles$Service;Ljava/lang/String;)V|PT-OPS-DBPORT-001,PT-OPS-DBPORT-002,PT-OPS-DBPORT-003,PT-OPS-DBPORT-004,PT-OPS-DBPORT-005,PT-OPS-DBPORT-006,PT-OPS-DBPORT-007,PT-OPS-DBPORT-008,PT-OPS-DBPORT-009,PT-OPS-DBPORT-010,PT-OPS-DBPORT-011,PT-OPS-DBPORT-012,PT-OPS-DBPORT-013,PT-OPS-DBPORT-014,PT-OPS-DBPORT-015|closed API/Web roles/canonical loopback URL and input invariants|
|ServiceDatabaseAdmission|verify (Ljava/sql/Connection;)V|PT-OPS-DBPORT-001,PT-OPS-DBPORT-003,PT-OPS-DBPORT-004,PT-OPS-DBPORT-005,PT-OPS-DBPORT-006,PT-OPS-DBPORT-007,PT-OPS-DBPORT-008,PT-OPS-DBPORT-009,PT-OPS-DBPORT-010,PT-OPS-DBPORT-011,PT-OPS-DBPORT-012,PT-OPS-DBPORT-013,PT-OPS-DBPORT-014,PT-OPS-DBPORT-015|borrowed connection state/one exact row/roles/db/recovery/owned reverse cleanup|
|ServiceDatabaseAdmission|unavailable ()Ljava/sql/SQLException;|PT-OPS-DBPORT-004,PT-OPS-DBPORT-005,PT-OPS-DBPORT-006,PT-OPS-DBPORT-007,PT-OPS-DBPORT-008|fixed08001 sanitized failures|
|ServiceDatabaseAdmission|required (Ljava/lang/Object;)Ljava/lang/Object;|PT-OPS-DBPORT-003,PT-OPS-DBPORT-005,PT-OPS-DBPORT-006,PT-OPS-DBPORT-007|nullable JDBC result/column contract fail closed|
|ServiceDatabaseAdmission|<clinit> ()V|PT-OPS-DBPORT-001,PT-OPS-DBPORT-002,PT-OPS-DBPORT-003|fixed URL/SQL policy linkage; first initialized testcase unknown|
|ServiceDatabaseSource|<init> (Ldev/codex/schubert/nk/storage/ServiceConfigFiles$Service;Ljava/lang/String;[C)V|PT-OPS-DBSRCPORT-001|public construction/close/closed gate only; default DriverManager not invoked|
|ServiceDatabaseSource|<init> (Ldev/codex/schubert/nk/storage/ServiceConfigFiles$Service;Ljava/lang/String;[CLdev/codex/schubert/nk/api/bootstrap/ServiceDatabaseSource$Connector;)V|PT-OPS-DBSRCPORT-002,PT-OPS-DBSRCPORT-003,PT-OPS-DBSRCPORT-004,PT-OPS-DBSRCPORT-005,PT-OPS-DBSRCPORT-006,PT-OPS-DBSRCPORT-007,PT-OPS-DBSRCPORT-008,PT-OPS-DBSRCPORT-009,PT-OPS-DBSRCPORT-010,PT-OPS-DBSRCPORT-011,PT-OPS-DBSRCPORT-012,PT-OPS-DBSRCPORT-013,PT-OPS-DBSRCPORT-014|owned password bounds/clone/consumption and supplied connector|
|ServiceDatabaseSource|getConnection ()Ljava/sql/Connection;|PT-OPS-DBSRCPORT-001,PT-OPS-DBSRCPORT-002,PT-OPS-DBSRCPORT-004,PT-OPS-DBSRCPORT-005,PT-OPS-DBSRCPORT-006,PT-OPS-DBSRCPORT-007,PT-OPS-DBSRCPORT-008,PT-OPS-DBSRCPORT-009,PT-OPS-DBSRCPORT-012,PT-OPS-DBSRCPORT-013,PT-OPS-DBSRCPORT-014|serialized physical source boundary/identity admission/Properties clear/caller ownership|
|ServiceDatabaseSource|discard (Ljava/sql/Connection;Ljava/lang/Throwable;)V|PT-OPS-DBSRCPORT-007,PT-OPS-DBSRCPORT-008,PT-OPS-DBSRCPORT-009|exactly one rejected connection close and local primary/fixed-secondary matrix|
|ServiceDatabaseSource|getConnection (Ljava/lang/String;Ljava/lang/String;)Ljava/sql/Connection;|PT-OPS-DBSRCPORT-010|credential override unsupported|
|ServiceDatabaseSource|getLogWriter ()Ljava/io/PrintWriter;|PT-OPS-DBSRCPORT-010|returns null, no writer acquisition|
|ServiceDatabaseSource|setLogWriter (Ljava/io/PrintWriter;)V|PT-OPS-DBSRCPORT-010|only null writer allowed|
|ServiceDatabaseSource|setLoginTimeout (I)V|PT-OPS-DBSRCPORT-010|fixed3 only, other signed boundaries unsupported|
|ServiceDatabaseSource|getLoginTimeout ()I|PT-OPS-DBSRCPORT-010|returns literal3|
|ServiceDatabaseSource|getParentLogger ()Ljava/util/logging/Logger;|PT-OPS-DBSRCPORT-010|fixed unsupported catalog|
|ServiceDatabaseSource|unwrap (Ljava/lang/Class;)Ljava/lang/Object;|PT-OPS-DBSRCPORT-011|self/interfaces exact identity, unrelated/null reject|
|ServiceDatabaseSource|isWrapperFor (Ljava/lang/Class;)Z|PT-OPS-DBSRCPORT-011|same type contract/null boundary|
|ServiceDatabaseSource|close ()V|PT-OPS-DBSRCPORT-001,PT-OPS-DBSRCPORT-002,PT-OPS-DBSRCPORT-012,PT-OPS-DBSRCPORT-013,PT-OPS-DBSRCPORT-014|idempotent own material cleanup, retained caller connections untouched|
|ServiceDatabaseSource|toString ()Ljava/lang/String;|PT-OPS-DBSRCPORT-001,PT-OPS-DBSRCPORT-010|fixed REDACTED output|
|ServiceDatabaseSource|unavailable ()Ljava/sql/SQLException;|PT-OPS-DBSRCPORT-001,PT-OPS-DBSRCPORT-005,PT-OPS-DBSRCPORT-006,PT-OPS-DBSRCPORT-007,PT-OPS-DBSRCPORT-009,PT-OPS-DBSRCPORT-012,PT-OPS-DBSRCPORT-014|fixed08001/no provider cause|
|ServiceDatabaseSource|unsupported ()Ljava/sql/SQLFeatureNotSupportedException;|PT-OPS-DBSRCPORT-010,PT-OPS-DBSRCPORT-011|fixed0A000/no provider cause|

Admissionはcanonical URL1/65535・DB名境界、API/Webのeffective/login role・一row・recovery false/null、borrowed connection設定、null statement/rowsと取得した資源だけの逆順close、固定08001、scope固有のunknown primary/固定secondary/両closeの優先順位を明示。Sourceは入力消費/clone1..65536・Properties四項目/clear・接続毎admission・一回discard・固定unsupported/wrapper/close・八独立task/get-close有限競合を明示した。

bootstrap固有の「既知SQLと未知close」「未知primaryと固定非秘密secondary」契約を旧3791/3793・SS342343に従って保持。別のordinary API SSC329等を当範囲へ上書きしない。SQL/Runtime/Error/self-throwable matrixはSource case009の独立identity/固定secondaryで追跡。scope違いを根拠にProductionを変更していない。

Admission synthetic enum switch helper1は元標準compiler filter/正常physical保持。Source Connector1は抽象NoCode。public default constructorは構築/close/closed gateのみ、元default DriverManager connector未呼出を独立postで保持。private heapの物理消去やJDBC immutable String完全消去・実PostgreSQL/role/grant/DB lock/commit/backend/全callee/G13/451を認定しない。元四counterはrun-levelでcase別probeではない。

新compile/JVM/Unit/JDBC/DriverManager/native/原本/credential取得0、新BUG0。対象12Source/67元測定methodすべての明示method-oracle linkが各群に揃った（未実測filter8/NoCode12は別）。この対応完了は全oracle/全Source/工程完了ではなく、正式1964PT53scope/unique517/候補114/pending12/whole93/newleaf0/工数null/G07未分類3313+22actualSecretCountnull/全HOLDは維持。次に別scopeの合成照合を行い重複/欠落を確認する。

command python3 -B evidence/01_PT/018_NK-OPS-001/input/643_database_method_oracle_review.py、日時 2026-11-08T16:22:26.947447+09:00、manifest `evidence/01_PT/018_NK-OPS-001/evidence/PG24122-database-twentyone-method-review-v1/manifest.json` SHA256 `ca3a8b334a45922db947126ba9e02f16124b6534a023876ce01a97c7503d336a`。各methodのSource/class SHA、Test ID/原case/要求/UI/承認SS pinと残存限界はmethod-oracle-relations.json。Source固定・通常pushはPG24124 publisher参照。
