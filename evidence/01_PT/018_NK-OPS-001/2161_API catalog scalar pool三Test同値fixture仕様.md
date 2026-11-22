# API catalog/scalar/pool三Test同値fixture PGPT仕様

NK-OPS-001/NK-MON-001、WBS-F03/群2524、原1/4/8週次枠pp/cap10、BUG1901/YKT1652/PG-D697。RD171/UI252/SS311342351、元仕様1635/1771/1773を独立正本として保持し、Main実装都合で期待値を変えない。

ApiMetricCatalogTest APICAT001..014（14）=独立16family/全SS layout/label許可・不正/未知/欠落/過剰/duplicate/null/immutablecopy/provider例外・並行。ApiScalarMetricExporterTest SCALAR001..024（24）=固定Prometheus text/有限counter/NaN gauge・null/type/duplicate/escape/deepcopy/一回read/checkedIOException/Runtime/Error・borrowed非close/並行二source。DbPoolMetricRecorderTest POOLMET001..008（8）=供給Counts3/5/2/8/未知NaN・真0・MAX/型/enum/不正/null/partialfactory・非close/並行same-instance/四系列上限。各class/method、fixture/入力/期待値根拠は元仕様表と元Test全文へ対応し、新manifestの原46method catalog/path/hashで追跡。

PG=元33raw中23Stringの意味名定数だけ、全元tokenへ逆復元、誤値・定数欠落・Test無効の九反例を拒否。他全input/Main不変。Test側literal/repeat/List/Map/固定数値をexpectedとし、Main出力からexpectedを生成しない。参照同一性比較二つはcopyと同instanceを区別する独立oracleなのでequalsへ変えない。Comparable二つとTHREAD六は実XML/source-localで確認し、未証明は未分類/全体pendingとしてraw保持。

normal六compile/packageでformat/NullAway/JSpecify/Werror（PT0）、source固定後原46method/三suiteを専用JVM240s・新所有空CWD/拡張・parallel自動無効で必要通常PT。一execを完全API467=実447+空metadata20へ照合、全Main1843不変/三SourceFile物理Test差/他byte不変、対象Main五の四counterと全API未達を実測する。除外/到達用assert/旧exec合成なし。PMD/CS実行、gate1や未達をPASS化しない。

command=11123 checked entry経由11180 plan/11182 inverse→11184 normal→11186原46→11188static→11190独立→原担当trace/2162。実時刻/OS/JDK/tool/source/branch/command/exit/全case/期待根拠/実測/XML/exec/hash/BUGを公開manifestに結合。実Hikari/SQL/DB/JMS/HTTP/service/Root/VM/native/実鍵/Browser0、原安全HOLD維持。新実装/PTは既成果の確認再演と区別し、正式1964/53・17/190・工数null・QA051final/全F03/451は更新を実証するまで未変更。

## 2026-11-22 現候補のAPIメトリクス検証仕様追補

対象Core 1e4e9e64830b552727043f3cb8b9435b28cba472、試験source cfbdb33c080224f54fbd3876b452b3945ac962b8。APICAT014／SCALAR024はメモリ内の固定16系統・2つの合成メータsource、4worker・各64件・各10秒上限。既存固定ラベル・カウンタ2/3、ゲージ5/7を期待し、終了とsource所有を確認。BUG-3554～3556／YKT-2800。新規選択は2成功・失敗0・除外0。残36個別は既存実行を候補のクラス・依存・JVM命令・固定入力へ照合。全体coverageと451は未判定。証跡 evidence/01_PT/018_NK-OPS-001/evidence/PG42144-f03-api-metrics-bounded-waits-v2/manifest.json SHA256 6fe65874fe6b4d08646d671cd778c036c4916f3073e6cec929fc650c0af0e3a4。

## 2026-11-22 API/Webプールfixture追補

POOLMET001～008／WEBPOOLMET001～008。試験対象は合成カウント・モード・借用providerのみ。各007は二回目の登録に固定のIllegalStateException／AssertionErrorを供給し、供給した同一実体、登録二回、所有リソースclose0、試験が所有するclose1を検証する。API/Web各006は有限待機の具体例外を宣言。v1通常16成功、v2定数名付与後の4 class実命令一致。BUG-3557～3562、YKT-2801/2802。evidence/01_PT/018_NK-OPS-001/evidence/PG42156-f03-current-pool-provider-fixture-v1/manifest.json SHA256 a3f99403d0618da567495596776f348431bf3e42bc17e9e073e6fe667df25f05。
