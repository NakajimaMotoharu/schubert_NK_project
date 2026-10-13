# NK-OPS-001 同run別fresh activation（SS343§6.13、SSC284）

関連RD OPS-009～017/DAT-009/AVL/BAK/BKO、UI251～252、SS341/343/353/354/355、451。Production3b7f3567b54f91f3a9dbeb859e8dd77e8353a2c8/PG2126/BOM62213f、元run91f/cutoff2026-10-13T15:01:53.237266Z、旧activation9beの真正終端・全24・正規ownedstop・独立post・当nativeは歴史成功、今回e142とは区別する。Current baseline/原本/Backup/private失敗scopeは不変更。

環境=LAN隔離VM Linux/current bootb2d6、Java25.0.4/PostgreSQL18、dev-foundation。工具はPython3、pyflakes3.4.0、独立7oracle＋graph/dispatch各1fixture。fixtureはProductionPT加点0、原本DB/秘密をGitへ公開しない。

| Test ID / program・method | 入力・fixture・操作 | 独立期待値／根拠／状態 |
|---|---|---|
| PT-OPS-PG2358-001 / observer.stage/watch | 実2356全post0、固定3file/hash、同署名/currentboot | 配置はobserverのみ。start/stop/reload0、元Root1800秒及び捕捉startからobserver期限1860を保持。stage実0、watch継続中 |
| PT-OPS-PG2360-001 / payload・external admission | 正常2352scope＋独立2356、元24/187/状態18/同runtime inode、一回fragment、初期四Unit kernel/job0 | 実宣言が固定runの二引数、同before6873c5eb/native9bf72ad・10execのみ、空き12GiB以上、observerの根/UID/argv/3hashを二読。durable reservationがstart前、一回explicit resume、新activationはProduction発行。client0は親合格でない。operator7b36f8b50・実0 |
| PT-OPS-PG2362-001 / body identity | captured MainPID104841/Job40474/Inv4011498e/start20469616839us | 同PID/ticks/UID/GID/argv、NKACT1/begin/run同値、同91f/cutoff保持、旧9be以外のUUID4、新e142。独立literal run/cutoff/旧activation/foreign反例4、実0/operator46f721d09 |
| PT-OPS-PG2364-001 / classify・payload | 同captured binding、DONE/独立PID1二読/current Unit | 正常0又は承認WARNING10だけ。旧run/activation/boot/job/inv/143/未知/部分GC/timeout/欠落/型null拒否。GC時のmanager observed=nullを0へ補完しない。DONE/PID1同世代・単調時計1800以内。独立4fixture及び多数field反例0、実未実行 |
| PT-OPS-PG2366-001 / qualify・all24 SQL | 封緘beforeの全column/固定24table、元progress一行/protected10/completed、元start以降 | 元全rowが同値のまま残る。次attempt=旧max+1、同業務日/run、九ALREADY_SUCCESSFUL SKIPPED＋CLEAN_INBOX_OUTBOX PROTECTED_RECORDS WARNING、四counter0。progress再初期化/削除0、HTTP匿名log/暗号session/SENT outboxは独立DDL/明示schema/相互joinで照合。再送による業務再発行拒否。3fixture/変更削除/誤attempt/unsent反例0、実未実行 |
| PT-OPS-PG2368-001 / capture・full seal | 真正2364＋2366＋2356 envelope/native封緘、同signed187 | 正常Ref10保持の中で全scope/currentsource/全32設定decl/状態18/DB24/原本Backup/metadata/187hash/署名を二読。Artemis/API/Web/Caddyの4owner PID-start/inv/argv/UID/GID/cgroup/budgetを捕捉。Root成功のみを全体成功にしない。fullsource静的/literal/非操作0、実未実行 |
| PT-OPS-PG2372-001 / sealed projection | 実2368 private before/hash | 封緘原本から親18fieldだけ抽出、現在Unit再読による旧像置換0。実未実行 |
| PT-OPS-PG2374-001 / emit・receipt | 同2368/2364/2362/2372 tuple、当15source | 本体positive binding後に独立receipt/negative旧9beを付加し、負vectorを正tupleへ変換0。全namespace/signed STEMpg2126/closure/static反例0。現実tuple生成/Java六ABI/配備は実未実行 |
| PT-OPS-PG2376-001 / stage・stop | 実2375全ABI/currenttuple/whole sealと親config二source | 新onlystage、正常M/A/DB/Ref、一回stop前にcurrent全proof・親projection・全scopeを二読。Caddy→Web→API→Artemisの正規owned TERM/所定期限・正常close、未知失敗は保持し強制kill/再stop0。独立dispatcher順序/禁制commands/closure fixture0、実未実行 |
| PT-OPS-PG2370-001 / metadata_lower_ns | Linux CLOCK_REALTIME_COARSE(5)、fine二採取、literal三inode | 旧fine105に対し実coarse100・inode100の正規境界を独立固定値で検証。任意margin/時計変更/unsupported fallback0。時計逆行/null/未知/余剰/範囲外拒否、精度誤差をinode/権限/byte弱化へ使わない。2fixture/cold2/normal-verifier1実0。現runtime再作成0、実new-cold認定は未完 |

実command=固定PYTHONPATHで各同名tools/quality scriptを使用。2358はstage/watch、一回2360、2362→真正終端後2364→2366→2368→2372→2375→2376 stage/stop→新独立post/native。停止後の同source CRC/session・新full3635との資格、CHR、Java四100%、適用JS、451、traceは別終了条件であり未受入。通常fixture/commitで工程を完了扱いしない。

関連BUG1231～1237/YKT997～1003（旧143/UNKNOWN/private表記は保全）、QA051最終比較保留。時計BUG1232は将来host是正のみ、旧2354 receiptのBUG1237は7b36f8b50で新生成だけ是正。公開数値・hashの現証跡は759/current-runtime-verification manifest、fresh結果は後記。source/command/exitの未確定値は推測せず未実行とする。
