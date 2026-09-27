# ServiceDatabaseSource単体テスト仕様書（PG287/D02）

Program NK-OPS-001。対象ServiceDatabaseSource constructor/getConnection/discard/closeとDataSource固定option、ApiJdbcPoolとの物理接続結線。RD SYS002/004/DAT001、UI212/243/253、SS342/343/SSC082追補・SSC084。共用境界移行と外部main結線は後続、Web roleの直接API module PTをWeb外部受入へ読み替えない。

fixture: 隔離PG18＋既存Flyway全migration、固定2role、公開合成password copy、公開JDBC interface proxyのみ。fixture PGはtrust認証で、本試験はSCRAM検証ではない（本番HBAのtrustは禁止されたまま）。driver password propertyの固定合成値・目的roleを独立assertし実秘密を使用しない。expectedはSS literal role/DB/Properties4値、所有close回数・入力array zero、固定08001/0A000から独立算出する。

| Test ID | 操作/fixture | 独立期待値・観点 |
|---|---|---|
| PT-OPS-DBSOURCE-001 | 両serviceの実role接続、source早期close/二重close、caller Connection保持 | 接続current_user/API=schubert_app・Web=schubert_web_session、database=postgres、単一row。constructor input消去、source close後の新規接続08001、既返却接続はcaller所有で非close |
| PT-OPS-DBSOURCE-002 | 固定source→Hikari pool→8物理接続を実借用 | 全8のadmission SQL各1回、固定user/password/connectTimeout3/ApplicationName、Properties全4項目だけ・使用後empty。再借用と物理新規を混同しない |
| PT-OPS-DBSOURCE-003 | connector null/SQL、実admin不一致、admission SQL＋close SQL | 返却0、取得済Connection close1回、raw cause/suppressedなし固定08001、Properties clear |
| PT-OPS-DBSOURCE-004 | 未知Runtime/NPE/Error bodyとSQL/同一例外/別Error close、SQL body＋未知close | 元unknown identity維持・固定secondary、既知body＋未知closeはunknown cleanup identity。close1回、結果なし、秘密診断なし、未知正常化なし |
| PT-OPS-DBSOURCE-005 | service/url/connector/array null、URL不正、空/65537拒否・65536文字上限、option/unwrap | constructor受領arrayは失敗時もzero、任意user/password/timeout/log出力拒否、wrapper限定、nullは境界NPE。char[]は既存strict decoder済みcopyを受ける内部契約。UTF-8 file byte境界はCREDREAD/Materialで別検証 |
| PT-OPS-DBSOURCE-006 | 8worker/32接続、公開source monitor保持中の別thread取得/close | 全task成功、private state lockで5秒内に完了、close後は08001、Connectionはcaller所有 |

選択command: JDK25.0.4で`./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -pl src/schubert-nk-api -Dtest=ServiceDatabaseSourceTest,ApiProcessMainTest,ApiNonSecretConfigTest,ApiConfigurationLoaderTest,ApiStartupInputsTest --no-transfer-progress test jacoco:report`。実source/hash/日時/exit/coverage・未実行scopeは090へ保存。秘密消去は所有char[]とProperties参照だけ、JDBC/JVM Stringまで消去保証しない。null・境界・SQL/provider例外・並行を満たし、全正式gate前は限定未認定とする。
