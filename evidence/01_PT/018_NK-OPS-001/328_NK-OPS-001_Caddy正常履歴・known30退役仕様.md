# NK-OPS-001：Caddy正常履歴と同世代known30退役（PG459）

関連RD SYS002004/OPS009/AVL、UI212251253、SS342 SSC178180・SS343 SSC136168179、QA047。Production=MorningCaddyReadiness cold/normal/number/unused/create/ready、BackupUnitStartClient.createCaddy、MorningStartupLaunchOwner.publishCompleted。工具はProduction PTへ加算しない。

| Test ID | 独立fixture/操作 | 期待値・根拠 |
|---|---|---|
| CADDY180001 | 固定manager literalの初回/no-historyと真正normal-history、legacy0/0、PID2/2147483647・U64最大 | SS342所定固定profile/初回空Invocationと未実行entry/正常history単一validate+run正常0、開始終了mono順序だけ受理。期待値をProductionから生成しない |
| CADDY180002 | 各field欠落/null/未知/異常・先頭0/負/overflow・PID1/2147483648・[n/a]/非normal/mono逆順 | IOException拒否、未知又は既存failureを正常化しない、NPEをcatchして成功にしない |
| CADDY180003 | 捕捉旧Invocationと新active別Invocation、同一/未知/null、active Result/code/status/mono改変、既存actor/socket/TLS後条件 | 新世代だけready、旧同世代を拒否、正常API/Webの所有条件を弱めない |
| PAIR459-PRESERVE | 現INVALID d536…の12file（current/現4/旧1eec…4/3intent）・各退役phase、文字が似たforeign name、旧保持4欠落 | 型付きWEB/API/publicationの厳密3件のみ退役、9非intentbyte/inode保持。BUG681のpublication unlink後に保存loopが欠落intentを読まない |
| PAIR459-CLOSE | A全呼出しpost-verify/closeにIO/Runtime/Error、変異前・後、再取得拒否/secondary close | 変異後は外M下で真正Aを再取得した場合だけ再quarantine、失敗secondaryはprimaryへ保持、M supervisor/非成功、旧A所有を推定0。全owned scope正常帰還後のみ完成印（BUG682） |
| PEER459-001 | 実PG458 readonlyspyを入力、固定PID/ticks/Invocation/source/info/母世代/ready欠落を独立改変 | 両真正Root→ordinary/API+Web200UP/info5・同peer/parent/socketを揃える、改変・未捕捉の代用拒否。工具だけのassert件数をProduction PTへ加算0 |
| NATIVE459-ISOLATE | 旧当boot/sourceea1/d041、親30/子143/PID0、Artemis生存、真正M/A/DB/全271x14/23business/原本pending/全Backup/Transfer/署名 | 固定逆順stopのみ、全9kernel空、原本/DB/Backup/startup不変、new permit/start/deploy/DDL0、旧失敗の成功化0 |
| NATIVE459-PAIR | 同物理全停止、私有14捕捉pin・全原値、typed already-invalid Pair、元owner/launch/世代、現+旧非intent | canonical既存Pairの3intent退役/sync、current INVALID/9file、全保存不変、全owned callback及び外M/A正常帰還。拒否/UNKNOWNは隔離保全・二重操作禁止 |

実行はhost JDK25.0.4/Maven3.9.12/Node24.19.0、独立工具javac -Xlint:all -Werror及び固定byte/hashの実VM閉集合（guest JDK25.0.4/PostgreSQL18.6）。選択10class→同変更群source固定fresh全6、host sourceとguest sourceea1の結果は分離する。current/permit/owner/rawspy/DBdump/旧原本/秘密はprivate root領域のみ、safe manifestにhash/固定結果だけ保存。329と456が現況。Coverage四counter100の要求は維持し、選択append exec・別source結果・未実行nativeを合格加算しない。native cold/generation/identity/socket/TLSの正常・例外・driftは同一新候補で後続再試験。
