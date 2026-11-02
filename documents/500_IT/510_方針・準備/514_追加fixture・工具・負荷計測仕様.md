# 再監査で追加したfixture・工具・負荷計測仕様

編集正本はcases.json（familyと期待結果）、scenarios.json（具体実行単位と証跡predicate）、contracts.json（SSの契約slice）。本書は工具実装者と実行Codexへの共通契約であり、実行commandではない。すべての追加工具は **UNIMPLEMENTED**。今回、工具を実装・実行していない。

既存[512](512_結合構成・環境・データ.md)・[513](513_工具・故障注入準備仕様.md)・[541](../540_実行・管理/541_Codex実行・判定・証跡・再開.md)・[542](../540_実行・管理/542_NG・修正・再試験・回帰.md)を継承する。依存PGPTの作業場・現用環境・過去の失敗世代へは一切注入しない。

## F-AUDIT-v2の構築契約

1. `design_commit/release_sha256/schema_version/config_sha256/protocol_registry_sha256/fixture_version`を実行manifestへ固定する。origin/main基準版と最終版のSS/承認変更/要件トレース/464を照合し、不一致なら実行前に仕様更新・レビューする。
2. 各SCは専有のDB/broker journal/Transfer/Asset/OSサービスを持つ隔離cloneで実行する。複数SCが同じ実DB、queue、サービス所有を共有しない。設計の正規queue名やpathを書換えて契約を変えず、隔離VM/namespace側で分離する。ネイティブFS/OS所有の試験では実Linux/ext4/SDS/FFMと正規UID/GID/ACLを使う。
3. fixture manifestに、論理alias→実PK/UUID/OS inode/queueの対応、全rowのbefore値、入力byteファイル、独立expected byte/件数/順序表を保存する。各SCの`initial_state`を必ず実体化する。抽象aliasを未解決のままdriverへ渡さない。
4. Message/operation tokenのalias M0/M1/T0等はSCごと別の正規nonzero UUIDとし、canonical UUID表をfixture作成時に一度だけ生成して固定する。M0とM1は異なる。W/Dは製品が生成した実UUIDを観測して対応付け、試験側が同じ値へ差替えない。header/property/source IDの各意味を区別する。M0を別SCのM0と共用しない。
5. `it_user1/it_user2`はUSER ACTIVE、`it_admin1/it_admin2`はADMIN ACTIVE、P-BASEはUSER8名+ADMIN2名（計10固有principal）。passwordは試験専用`ItOnly-20261101!`、実Loginでcontext/CSRF/cookieを取得する。secretはprivate artifactへだけ保存し公開索引にはhash/aliasを置く。SSの最大2sessionを超える並列Loginを同じuserで代用しない。
6. UCRはusernameをSC固有の`it_<case suffix>_<SC番号>`、role USER、status ACTIVE、passwordを上記試験値とする。field名/target/version/tokenのwire表はUI235/236・SS323の正規layoutを使う。故障前に別のUCRを成功させ、当SCで使用する入力とは別名で入口接続の検査をする。成功を対象SCの結果へ数えない。
7. QSBはquestion本文`IT-AUDIT <SC-ID> 質問`、owner=実Login user1、他の必須fieldはUI236の確定表からfixture manifestへ展開する。Q0/job/notification/answerのPKと状態は、SCが求める到達点まで実受付・実worker/CASを通して構築する。意図的な不整合fixture以外で直接DMLだけを使い、実部品の前段を検証した扱いにしない。
8. SCN201/10000は独立作成した順序表 `(entry_order,audio_order,logical_ID,全wire field)` 201/10000行、各record4800byte。元snapshotのmetadata8論理fieldとrecord全byte/hashを固定する。変更fixtureは8field中の指定1field又は201行目の1byteのみ差分を保存する。8field名と固定入力は515で具体化済み。実manifest生成・review完了までPREP-DATAは解除しない。正本masterを使う場合はそのmanifest/hashと選択集合を固定し、実装の検索結果をexpected集合として採用しない。
9. 通常Rangeはtotal2097169、独立pattern `byte[i]=i%251`、大きいMediaは48000001byte。実Assetで論理descriptor/hash/size/権限を整合させる。download表示名256ASCIIと実segment `asset.bin` は別field。正規Media type/実URLはIF009/012/016のregistryからfixtureへ解決し、未解決なら開始不可。
10. Log fixtureは固有keywordで隔離し、INFO/WARN/ERROR/DEBUG/TRACEの5行。Login/setupのログをtotalへ混入させない。診断のみは別keyword。logged_at/idの固定表で順序とcount/listを独立照合する。
11. Outbox/Inbox fixtureは実DDLを使う。due/lease/created/completed/expiry、暗号keyVersion、AAD owner/layout/sourceをすべてmanifestへ保存する。暗号fixture生成・復号検算は独立JCE等で仕様から作り、対象のsnapshot encoder/decoderで両側を生成しない。破損tag/旧raw/不一致metadataは改変前後byte/hashを保存する。製品の暗号保護を無効化しない。
12. BackupはSS341の実dump・config/credential archive・manifest等の全4fileとDB二stepの完全pairを必要とする。成功/再用/fresh SKIP/新失敗のattemptを別IDで管理する。全schema、hash、UID/ACL、実 `pg_restore --list` の存在・用途は実行準備時に検証する。restore/private keyの承認HOLDは維持する。

未確定の具体検索predicate/正本master選択集合はISS-SELECTIVITY/ISS-DATAへ分離する。fixture作成の未実装と、設計oracle未確定を混同しない。入力が解決していないケースは実行可能としない。

## T-FAULT-v2：一回故障注入・barrier

これは実装すべき接口仕様で、呼出可能なCLI名は未定義。PG/PT中の工具へ接続しない。将来工具を実装する際は、製品artifactのhashを保つ外部proxy/実OS障害を優先し、必要な計測buildはreleaseとの差分と観測影響をレビューする。計測buildだけの成功を最終releaseへ転記しない。

入力レコード：`run_id,scenario_id,attempt_id,source_sha,artifact_sha,environment_id,boot_id,unit,invocation_id,pid,start_ticks,owner_nonce,point,phase,occurrence,max_wait_ms,effect,release_policy`。

- pointはSC本文の確定点。`DB commit-visible / client-ack-before`、`claim-commit-after / send-before`、`answer-insert-before`、`publish-success / fsync-before`、`Root final close`等を別名で識別する。単なるmethod名到達やsleepをcommit証拠へしない。
- receiptは上記全identityに`sequence,monotonic_ns,utc,transaction_id,message_id,token_hash,resource_owner,inode/dev,observed_state,receipt_sha256`を加える。armed→reached→effect_applied→released→terminalを一回だけ記録する。未到達ならNOT_JUDGED/BLOCKED、故障が効いていない成功を合格にしない。
- 専有部品以外のPID/backend/Unit/portに作用しない。barrier直前・直後にboot/PID-start/Invocation/所有nonceを再照合し、変化時は注入しない。故障後の無条件再start/ACK/COMMIT/rename/unlinkは禁止。
- DB commit ACK喪失はserver commit可視化とclient完了を独立観測する。内部関数mockで「commitした」と返す方法は実commit不明を検証しない。実注入設計は515 T-COMMIT-v3。工具実装・校正/レビューはISS-COMMIT-INJECTION（D）で未完了。
- broker durable commitとproducer確認、受信ACKと業務DBcommitをそれぞれ記録する。明示PAGE上限はFAIL、disk90%はBLOCKであり同一oracleにしない。
- 真正OSのclose失敗/送達不明を安全に再現できない場合は未実施範囲として残す。値オブジェクト/例外だけのPTを実所有close ITのPASSへしない。

## T-DB/T-COLLECT-v2：独立readbackと最小証跡

未実装の検証SQL packは、最終SS331/332の実列に解決してレビューする。対象の更新SQL/判定関数をexpected生成へ呼び出さない。

| pack | 必須projection/集計 | 判定 |
|---|---|---|
| command-atomic | request_inboxのMessage/owner/token/HMAC/layout/state/result/body hash/ref/completed/expiry、対象user、critical audit全row | Message/token別before→afterの件数と全field差分。command/user/audit/inboxの同一確定点、rollback時新規0 |
| async-state | async_jobsのstate/processing_message_id/retry_count/全時刻、questions/answers/notificationsのPK/owner/deletion triple、Outbox D/W | W/D/M0を別join、answer question_id UK1、completion µs同一、final D SENT前ACK0 |
| snapshot-replace | request_inbox全19列before/after、response encrypted hash/keyVersion | 置換2列以外17列完全一致、初回completed/expiry不変。暗号検算は独立AADと保存元Message |
| outbox-lease | Message/status/owner/lease_until/next_attempt/attempts/created/sent、claim TX、JMS commit receipt | claim<=100/10秒lease、application delay base1/5/30/60/300秒±10%jitter、SENTは送信確認後 |
| cleanup | run/step全identity/count/ended、progress/cursor/hold/eligible存在、削除前PK集合と削除後集合 | 同TX DELETE+累積、LOCK_BUSY未完了、元cutoff保持、未確定件数NULL/UNKNOWN |
| backup-expiry | 旧元SUCCESSと新SKIP/FAILED pair、4file inode/hash、expiry before/after/cutoff/selector | 同attempt完全pair、再用再生成0、削除/再purgeの所有と許可、未知after=NULL |
| permissions | 実接続role、実行statement/management action、結果SQLstate/provider errorと非秘密分類 | allow/denyと更新0。資格情報本文を証跡公開へ含めない |

各SCの`assertion_evidence`はattempt root相対pathとpredicateを持つ。`db.jsonl`等の共有artifactには少なくともevent種別・before/after・全join keyを保存する。assertion判定recordは`test_id,scenario_id,attempt_id,assertion_id,source,expected_ref,actual_fields,evidence_path,sha256,status,reason`。証跡ファイルを列挙しただけで合格にしない。各predicateの抽出field/対象PK/時刻/許容差をcollector実装レビューで確認し、不足時はNOT_JUDGED。

秘密canaryはprivate row/暗号fixtureへ入れ、公開HTTP/local log/metric label/証跡索引へ出現0を独立byte検索する。公開証跡へraw認証context/password/鍵を載せない。必要な原失敗のprivate証跡とredacted索引をhashで結ぶ。

## T-LOAD-v2：性能・負荷計測

負荷の正本は各SCの`load_plan`と`initial_state`。後者の個別条件を優先する。300秒warm-upは計測準備の入力でSLA免除期間の新設ではない。正常対照と混在窓は同source/fixture/設定/同期間・同client数・同seed。QA050は各45分、900秒定常を少なくとも2周期実時間で含む。2回反復をSC数へ加算しない。

- closed loopは各固有userにつき1inflight、完了後に次を発行。throughputは結果として測る。burstは10秒ごと10名一斉で、前試行未完ならslot欠落として記録し、同時上限を超えて追い付かせない。架空の一定requests/secを保証しない。
- 60/20/10/10のmixは100slot周期にsearch60/game20/QSB10/NTS10。USER8人の合計80slotはsearch44/game16/QSB10/NTS10、ADMIN2人の20slotはsearch16/game4。1client10slot単位でfixture seedとslot割当表を固定する。比率の達成を完了率から推測しない。rampの70/20/10ではUSER計80slot=search64/game16、ADMIN20slot=search6/game4/Log10。
- QSBの回答が外部provider依存なら、fixtureの固定表と隔離provider simulatorを明示する。実worker/MQ/DB/transaction/時刻/ACKを検証し、外部providerの本番性能・可用性は保証しない。provider実接続を要求するSS条件は別未実施範囲として残し、ST受入と切り分ける。
- E2EはWeb操作開始→response/描画終端、MQ待ちはrequest開始→対応reply、SQLは独立query begin→end。対象関数の自己申告だけで両側を測らない。生のmonotonic時刻・UTC・clock同期誤差を保存する。
- p95は各routeの全試行elapsed昇順の`ceil(.95*N)`番。N=0はNOT_JUDGED。timeoutは打切値とcensored=trueを記録し、率の分母へ残す。成功試行だけのp95と全試行の率を併記する。失敗がある場合、p95だけで全SC合格にしない。API同期2秒とE2E2.5秒、SQL1.5秒を混同しない。
- throughput/error率/timeout率とp50/p95/p99/max、queue wait/depth/oldest/drain、CPU/RSS/heap/direct/metaspace/GC/thread/FD、DBpool/lock/WAL、journal/paging/disk I/Oを同窓で採取。計画停止・故障窓は明示して全rawを残す。除外できるSLA対象範囲はRD/UI/SS原文に従い、復旧直後を任意に免除しない。
- GC/agent/JDK生成要素を起因にする件数/stack shape/metric増加を、そのまま業務NGとしない。STANDARDの計測overhead対照・生成要素の根拠・計測器版を保存する。coverage agent/JFR等の追加計測窓は性能本判定窓と区別し、必要なら同sourceのSTANDARD窓で再測定する。観測値を都合よく除外する閾値は追加しない。
- SSにないthroughput下限、許容error率、劣化率%、メモリ傾き閾値を新設しない。既存MemoryMax/資源予算/同時上限/byte上限/SLAと質量収支で判定する。基準未規定の収束時間等は実数を保存し設計判断へ渡す。
- 性能NGの調査は発行/待ち/DBlock/pool/JMS/file/GC/計測器を原証跡で分解する。timeout延長/上限拡大/再試行間隔変更で救済しない。QA050で間隔調整が必要なら承認済み変更→SS/config/case/review更新→同normal対照と混在窓の再測定を新attemptで行う。

## 中断・再開とNG管理

予約キーは`source/artifact/environment/boot/case/SC/fixture/attempt/owner`。job registryとbarrier receipt、DB/JMS/inode/Unitの途中状態を読取り照合し、同jobへ再付着する。job不明やsource/env違いでは自動再発行しない。送達/commit不明の読取り照合完了前に新Message/新token/新Unit startを出さない。

初回NG/UNKNOWNを保持し、542のPG不備/SS不備/試験側/環境/上位判断/未判定を証拠で分類する。仕様監査で見つけた不足は実測NGへ登録しない。修正後は当該SC、同契約の他parameter、共有結合経路、DB/JMS/file確定点の隣接caseを影響graphで選ぶ。PG915/916、SS914、上位911～913の用途を守る。工具/期待値修正でも原失敗を上書きしない。

継続監査での具体化・訂正は[515](515_継続監査のfixture・probe・故障注入準備仕様.md)を参照。Dの実生成/工具準備が終わるまで実行不可。
