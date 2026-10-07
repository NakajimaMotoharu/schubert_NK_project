# PG505 同source外部Morning・真正親受入PT仕様（実行前）

02:28実終端更新：006 v3 actual0・全原値二読/452=442+10SKIP、safe manifest=`evidence/provisional/PG505-failure-readonly-v1/manifest.json`。002stage0/003一回client0、004真正親timeout143/005DONE未達・A01NOT-RUN2。PG512独立current-boot API journalによるordinary-api193 namespace ENOENT5回でBUG813→814原因実証、Expiry通過/残留APIintentを認証。Broker段推測は撤回。未実行表は開始時の初期状態の履歴であり、この追記の失敗を合格へ変更しない。旧v1v2/SAVE前拒否を保持し、成功commandはpg505_capture_failure_v3.pyへ対応。

006 v2はbatch_runsに存在しないcutoffキーを参照してSAVE0拒否（BUG815 oracle列照合の同修正範囲）。SS331/332実DDLの全17columnではcutoffは同runの別原本、batch_runsはbusiness_dateを持つ。既baseline当run一意business_dateを独立Oracleとし元run/cutoffは保持active/NKACT1と別照合、prototypeのcutoff参照を実DB結果の都合で残さない。new-only v3に固定10SKIP/ALREADY_SUCCESSFUL/zero4counts/既一意dateを正しく対応する。未成功v1v2/source拒否を保全、署名/source・元期待仕様不変更。

現実結果=新親元1800sでtimeout143/全RootAPI-Web/Caddy未起動/DONE未受入、observer0は親合格に加算0、A01actual2/not-run。BUG814/YKT583。過程ExpiryにもSKIPを記録したことを新SQL独立照合で確認し、未起動APIから前段未達を推定しない。
PT-OPS-PG505-006：当新failure cohort/全10Unit/full18/全現在PID/INV/ticks/argvSHA/authorityを二読しfull24table全列と全tree/current/config・nativeをRoot私有捕捉。元442全row/他23table/永続102不変、追加は固定10段同日成功SKIP各一件（BACKUP2/Cleanup7/Expiry1）、元run/cutoff・zero4counts・ALREADY_SUCCESSFUL/ended>=started。理由textはSS341同日成功SKIPの内部補足として独立literal `step already successful for business date` を固定（既BatchStepResult由来の表記を手動照合、production methodによるexpected生成0）。旧ReasonNULL/9段のtool初期oracle拒否はBUG815/YKT584・SAVE0/DB変異0を保持。command=guest readonly python3 < tools/quality/vm/050_s1/pg505_capture_failure_v2.py（一回新SAVE・二読、旧v1不変更）。raw DB/original/native/sessionはGit0、結果exit/hash/count/不合格/保全pathだけsafe evidence。

NK-OPS-001/NK-BAT-001/NK-API-001/NK-WEB-001、WBS-N01/N05～N12/N14/N15・G13.07。RD SYS/ENV/PER/AVL/OPS/MONの485主担当join、UI211212/231/243/251253、SS311331332341～355/SSC198202203206208・QA047、BUG799関連。
Productiona2/PG495全3411/510suite/static6zeroは限定host、current正式run24/1964/53scope不変更。
前提=PG504 freshruntime全新scope正常/complete SHAac7a0eb9af359638ed84bab5951afe69cfc2636e2b460233f82029560aa762ad、after SHA67fa28ad6f289589994af0be7022a20fe12b673685d0c151ffb791dd91fec52e、当bootcc9/全10cold/原全24table442batch/原本BackupTransfer/全volatile/native・INVALID・全config保持、旧scope UNKNOWN/143を代入0。

| Test ID | 操作・fixture | 独立期待値/根拠 | 初期状態 |
|---|---|---|---|
| PT-OPS-PG505-001 | stable_actor20/authenticate_ready4独立owner/race/identity vectors | 旧同source結果転用でなく同byte再実行。manager/kernel sandwich・Root ordinary同peer/UID/GID/groups/caps/NNP/HTTPinfo/socket拒否 | host20/4正常、ProductionPT加算0 |
| PT-OPS-PG505-002 | 新observer Root400/boot/source/署名/current・全10cold/準備receiptを認証 | fixed3Python exacthash/new-only、observerはread-only/start-stop0/元親deadlineを延長しない | 未実行 |
| PT-OPS-PG505-003 | 全元原値/config/runtime/peer-advisory-MA0二読、native-before私有保全、durable一回予約→systemctl外部start一回 | same run91/元cutoffは保持activationから独立照合、元budget1800s。clientExit0は親成功ではない。guard後deliveryUNKNOWNは再発行0 | 未実行 |
| PT-OPS-PG505-004 | 同親/元Backup原本通常再用/新同runSKIP・Cleanup/issuer/親Rootとordinary API→API所有保持Web→Caddy | genuine manager INV/PID/ticks/boot、HTTP200UPとinfo(a2/schema028)、socket同owner・Root普通同世代、TLS公開CA/hostname有効/login200/表示schubert NK。rawbody/session/credential保存0 | 未実行 |
| PT-OPS-PG505-005 | 親真正DONE/元30min/全保持原本・intent正常完了、終端Root証跡 | parent code/exit0/DONEを実証、API ready/途中TLS/command0/observer0/143だけで合格0。owned逆順停止/全資源後条件/native同sourceは次の別認証工程まで未受入 | 未実行 |

commands: python3 -B tools/quality/vm/050_s1/pg505_prepare_observer_v1.py; bash tools/quality/vm/050_s1/pg505_parent_observer_v1.sh（新only一回/付着後継続）; python3 -B tools/quality/vm/050_s1/pg505_external_resume_once.py（上記全前提とdurable guard成立時一回）。既guard/start存在時は再実行禁止、現在INV/job/logへ付着。親/Unit期限をrenewしない。全fault/再送/null/coverage100/全CHR/正式/IT-STを当部分成功から宣言しない。失敗はBUG/YKTへ修正前登録し原証跡を保持、私有DB原値/native/rawsessionはGit禁止。
