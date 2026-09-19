# NK-OPS-001 PostgreSQL配備設定単体テスト仕様書

BUG209のnative enum換算根拠: [PostgreSQL18 WAL](https://www.postgresql.org/docs/18/runtime-config-wal.html#GUC-WAL-COMPRESSION)はonをpglzの旧表記として規定する。literal設定はonのまま、native期待だけpglzとする。得られた実際値を無根拠に期待へコピーしない。

着手時発見BUG208/YKT164: 既存001_rolesには6roleの18timeoutが未設定。PGCFG005は修正前catalogを反例として記録し、SS342既定値を実装後再試験する。前提の「既存設定済み」は誤りであり、期待値を現状へ緩和しない。

PG-D-187/SSC-069。RD SYS005～014/DAT003/PER/ENV、UI212/253、SS342§6/351。対象src/deployment/postgresqlの2雛形、PostgresDeploymentTest各method。既存role timeoutは001_roles.sqlの実適用後catalogを検証しDDL/grantを変更しない。

| Test ID（PT-OPS-） | method | 入力・操作 | 独立期待・算出根拠 |
|---|---|---|---|
| PGCFG001 | literalConfiguration | UTF8 confの非comment全directiveをparse | SS342から手書きした完全map、重複/欠落/余分0 |
| PGCFG002 | nativeConfiguration | 隔離cluster data＋雛形をpostgres -Cで各値照会 | SS単位をPG18出力単位へ独立換算したmap。server起動/2GB割当なし |
| PGCFG003 | literalHba | HBA非comment全行読取 | peer1＋業務5role×2＋migration2＋inspector1＋reject2＝16、完全順序一致 |
| PGCFG004 | nativeHba | 自分の隔離cluster HBAを一時差替しpg_hba_file_rules照会、finally復元、reloadなし | 16行/error NULL、種別/DB/role/IP/netmask/auth完全一致、実host不変更 |
| PGCFG005 | roleTimeouts | 既存Flyway/provisioning後pg_roles.rolconfig照会 | SS342§6.2の6role×3値＋inspector2値、既存未規定idleを設定済みとしない |
| PGCFG006 | invalidConfiguration | unknown GUC/不正syntaxをnative parse、global bind/SQL logging/missingをliteral policyへ注入 | native非zero、policy不一致。policyはtest-only、runtime validator実装とはしない |
| PGCFG007 | invalidHba | 不正auth native parse、trust/md5/remote/missing rejectを独立policy比較 | native error、policy不一致、元HBA復元 |
| PGCFG008 | isolationAndEvidence | fixture path/接続先/元HBA・設定公開値のsanitized trace | 対象はtest用loopback/target配下、元HBA復元、秘密/raw DB logコピー0 |

fixtureはApiLogDatabaseFixtureの新規専用cluster、既存production Flyway。null/欠落/未知/重複は設定inventory照合、例外時HBA復元。静的宣言に並行/再送の業務分岐はなく、本PTで実deployment/認証通信/IT性能/全secret gateを認定しない。既存Java全line/method/class/branch100%を維持、設定にはJava coverageを適用せず全directive/規則を照合（除外追加なし）。

commandはJDK25.0.4/Maven3.9.12 offlineの選択PostgresDeploymentTest後、全clean verify。実日時/commit/結果/coverage/hashは034とevidence/manifest.jsonへ成功後記録。未実行を合格に算入しない。独立期待はproductionを呼んで生成しない。native出力は公開設定値のみ、stderr/raw logは証跡へ格納しない。
