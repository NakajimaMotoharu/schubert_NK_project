# PG475同source接続・停止仕様

Program NK-OPS-001、PG-D380、SS342/343/352/355・SSC190/191/193/194/195、RD SYS002004/OPS009/MQ003006008010/TST004、UI212213251253264。既363/368/370と同じ承認済契約をsource979c5ac3e9c28ae76363adacdf9f0736f5a59df1で閉じる。旧結果流用、Current変更、未承認DIF、Production対象除外0。

|Test ID|入力・操作・独立期待値／command|
|---|---|
|PT-OPS-CODE475001～004|停止済PG474の真正receipt・同boot/current/原本DONEを再認証。新署名PG475/186artifact/187canonical/27SQL・全6frozen byte一致。M/A/DB下で401全14/全23business/原本Backup/61metadataを保全し、新INVALID/code-only切替のみ。21exec＋2heap全23actual byte/metadata archive、旧0byte execは成功扱いしない。pg475_stopped_verify_v1.sh→activate→collect_stopped、start/stop/permit/DDL0、全newscope通常帰還が期待。独立Java71/Python153/inventory41、null/foreign/欠落・改変・mode/identity・順序・close不確定等を拒否。|
|PT-OPS-PG475-PARENT001|Root400 observer先行→pg475_external_start_once.pyのguard付き外部Morning一回→親3145979/7f489e7c728a4f22a6138be4ef96d3f8/job223578/startmono212820166772。元30分期限を更新しない。実Root→普通API/Webの同PID/generation/parent/INFO5/UIDGID/groups/zeroCaps/NNP/socket、Caddy公開CA/TLSlogin200、同bootの真正PID1 DONE1を固定window03:26:09～03:56:10 UTCで確認する。APIready/client0は親成功ではない。|
|PT-OPS-PG475-READ001/002|捕捉したactualpeerだけへ固定したpg475_readback_native_v1.sh。旧401全14原値と新411の追加10technical SKIPPED/affected0、65metadata=16全group＋epoch、旧60byte/metadata・全原本Backup・全newscope通常帰還。ADMIN1/authcontext8は今回起動前の実fixture、contexts数を同時session上限と混同しない。独立432vectorでnull/欠落/foreign/時刻境界/構造/metadata等を拒否。draft工具は配置しない。|
|PT-OPS-PG475-CHR001|pg475_a01_native_v1.shはshared Current A01/固定baseline+DIF001QA045だけで比較。pg475_l01_native_v1.shは私有観測のみ、QA051未承認の比較をPASSへ変更しない。credential変更/reset、baseline上書き、missing/duplicate免責0。|
|PT-OPS-PG475-TERM001/002|pg475_native_stop_v1.sh、同捕捉4peer/full journalと8Unitの逆順owned停止。ordinary143は全後条件/journal/native付き停止データ（Unit successにはしない）、依存終了への二重stop0/全9kernel空。postL01全business/411/原本Backup/65metadata/epoch不変、全newscope通常帰還。独立Java24/control265/TERM240、旧UNKNOWN正常化0。|
|PT-OPS-PG475-NATIVE001|pg475_collect_native_v1.py→native_gap→collect_connection。新8single sessionのみ、Root普通4roleID/元時間window/mode600/専用UIDGID/同6frozen byte/全classNoMatch0。全counter未達は残件、nativeだけで正式全scope合格へ加算0。|

fixtureは隔離PG/PT VMの既存実DB/原本Backup/current専用account及び正規署名・permit・Production入口。OS/JDK/toolchainは451/421、branch dev-foundation。工具assertionはProduction PT件数0。raw DB/session/token/credential/heap/execをGitへ格納しない。actual時刻/exit/source/command/hash/BUG/SSC/coverageは373とsafe manifestへTest IDで対応する。未実行・途中・別sourceの成功は合格算入しない。IT/ST後続。
