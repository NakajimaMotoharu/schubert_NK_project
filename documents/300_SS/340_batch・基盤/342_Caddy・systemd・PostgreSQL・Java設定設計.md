# Caddy・systemd・PostgreSQL・Java設定設計

## 1. 目的・状態

Caddy、systemd、PostgreSQL、Artemis、Web/API/batch Java processの初期実効値、入力file、port、resource上限、
hardening、timeout/readinessと検証方法を定める。

- 状態: `確定`。Artemis再配送・容量とDB backup role分離はQA-041～043/UIC-001～003承認済み
- 上位設計: UI 211～212、231、251～253
- 関連RD: SYS-002～SYS-004、SYS-012～SYS-014、OPS-001～OPS-012、MON-001～MON-013、
  PER-001～PER-010、AVL-001～AVL-010
- 関連QA/RDF/UIC: QA-007、QA-010～QA-011、QA-016、QA-021～QA-022、QA-027、QA-029、QA-041～QA-043、RDFなし、UIC-001～UIC-003
- 関連SS: [321_Artemis物理構成・JMS設定設計](../320_メッセージング/321_Artemis物理構成・JMS設定設計.md)、
  [341_朝batch・backup・削除・再実行設計](341_朝batch・backup・削除・再実行設計.md)

## 2. Host・network・port

| Component | Bind/default | Public firewall | 備考 |
|---|---|---|---|
| Caddy HTTPS | `<global-ip>:55160` | allow 55160/tcpだけ | TLS終端、初期internal certificate |
| Web HTTP | `127.0.0.1:8080` | deny | Caddyからだけ |
| Web management | `127.0.0.1:8081` | deny | health/readiness/metrics、Caddy非proxy |
| API application HTTP | disabled | deny | Browser/HTTP APIを持たない |
| API management | `127.0.0.1:8091` | deny | health/readiness/metrics |
| Artemis CORE/JMS | `127.0.0.1:61616` | deny | Web/APIのみ |
| Artemis console | `127.0.0.1:8161` | deny | OS tunnelと専用管理credential |
| PostgreSQL | `127.0.0.1:5432`,`[::1]:5432` | deny | app/migration/batchのみ |

OS firewallはdefault deny inbound、55160/tcpのみallow。Loopback serviceを`0.0.0.0`/`::`へbindしない。
Port変更はconfig manifestを更新し、firewall・Caddy・client URL・health probe・ITを一括反映する。

## 3. Caddy

### 3.1 Caddyfile論理形

`<GLOBAL_IP>`、certificate、upstreamは配備時にrenderし、Gitはplaceholder付きtemplateを管理する。

```caddyfile
https://<GLOBAL_IP>:55160 {
    bind <GLOBAL_IP>
    tls internal

    request_body {
        max_size 2MB
    }

    header {
        Strict-Transport-Security "max-age=31536000"
        X-Content-Type-Options "nosniff"
        X-Frame-Options "DENY"
        Referrer-Policy "same-origin"
        -Server
    }

    reverse_proxy 127.0.0.1:8080 {
        header_up X-Forwarded-For {remote_host}
        header_up X-Forwarded-Proto {scheme}
        header_up X-Forwarded-Host {host}
        transport http {
            dial_timeout 2s
            response_header_timeout 30s
            read_timeout 60s
            write_timeout 60s
        }
    }
}
```

- `file_server`、asset/transfer root、Caddyの直接media配信を定義しない。
- Caddyは外部から受けた`Forwarded`/`X-Forwarded-*`を信用せず、直接peerから再構成する。前段proxyなしのため
  `trusted_proxies`を設定しない。Webはremote addressがloopbackの場合だけCaddy headerを採用。
- CSPは352 §7.2のfixed allowlistをWebが設定し、Caddyで上書きしない。Inline script/styleを許容しないためnonceも使用しない。
- Access logはJSON、path/status/duration/bytes/remote IP/request IDだけ。Cookie、Authorization、query string、request/response bodyを
  filter除外する。Filter非対応の導入minorではaccess logを最小化し、Web WLGEVT01を業務監査正本とする。

### 3.2 TLS・検証

- QA-022に従い初期はCaddy internal CA/IP certificate。警告を許容するがHTTPへdowngradeしない。
- Private keyはCaddy専用state/credential、root/Caddyのみ読取。Fingerprint、有効期限、検証手順をconfig manifestへ記録。
- Domain/公的証明書移行時はsite address/TLSだけ変更。`tls_insecure_skip_verify`はupstream/clientとも使わない。
- Deploy前に`caddy fmt --diff`、`caddy adapt --validate`、`caddy validate`、起動後TLS/header/loopback upstreamを試験。

## 4. Systemd dependency・unit設定

SSC101/PG318: Caddy package実Unitの既定 `SendSIGKILL=yes` を親保守停止へ採用しない。NK専用非起動drop-inで `SendSIGKILL=no` と `TimeoutStopSec=30s` を設定し、daemon-reload後の実効 Id/LoadState/KillMode/SendSIGKILL を親の固定8対象と同じ閉集合で確認する。既定Caddyを実測せずにpolicy合格としない。policy確認はstop client/全cgroup終端/Artemis journalの代用でなく、未配置Unitのfake/alias禁止を維持する。

### 4.1 Dependency

| Unit | `After` | `Requires` | `Wants`/note |
|---|---|---|---|
| `schubert-nk-backup` | PostgreSQL | PostgreSQL | 失敗はmorning続行 |
| `schubert-nk-cleanup` | backup | PostgreSQL | Backup成否はDB rowで分岐 |
| `artemis` | cleanup | cleanup | Cleanup safety failureで起動不可 |
| `schubert-nk-expiry-cleanup.service` | Artemis | Artemis | API Consumer前に実行。SSC099: SS341§2の完全名、別名expiry-cleanup.serviceを作らない |
| `schubert-nk-api` | expiry, Artemis, PostgreSQL | Artemis, PostgreSQL, expiry | readiness poll後にWeb |
| `schubert-nk-web` | API, Artemis, PostgreSQL | API, Artemis, PostgreSQL | technical DBが必要 |
| `caddy` | Web | Web | Packageの自由先行起動をdisable |

SSC104/PG324：上表Cleanupはroot MorningがM/A保持中に同期起動する真正oneshotであり、空の成功Unitを置かない。固定非秘密requestはsystemd `LoadCredential`でprivate受渡しし、`db-batch`はroot Cleanup専用processへ固定配布する。Unitの0/10は実削除・skip/警告・transferを記録した親検証済終端だけに対応し、safety failure/起動不明は非成功でArtemis `Requires`を遮断する。root実行権限は現物backup root/原本検証のためだけで、shell/任意argv/env/Secret出力は禁止。service templateの完成・配備は全親/子契約と別PTを経るまで未認定。

`schubert-nk-morning.target`が全unitをWantsし、通常bootの`multi-user.target`からWantsする。BackupのFAILEDは
target全体を止めず、cleanupが削除skipを記録した上で後続する。

### 4.2 Java service共通

SSC-087: root前段も共通sandbox内で動き、ProtectSystem=strictを解除する`+`/shell/setnsは使わない。PrivateUsers/PrivatePIDsや固定permit fileの古いbindを追加せず、PID1/system managerが同じhost/bootであることを検証する。root前段のread-only保持host能力だけで現在host FSを観測し、exec前に全closeする。普通serviceにはA短期FDとsealed公開proof以外のhost能力を移さない。private RO観測をhost故障のRO状態と混同しない。

SSC-086: 完成時の直接Java入口は同Unit/same PIDのroot前段`RootServiceLauncher`とする（ExecStartの`!` prefix、shellなし）。前段は既存root起動管理の全root/Ops/schema/現在起動許可をread-only検査し、native execveで固定`/usr/bin/setpriv`→固定`/usr/bin/java`→従来service mainへ置換する。!はSupplementaryGroupsも無効化するので、固定account/groupのNSS解決値を明示`--reuid/--regid/--groups`へ渡す。init-groups/任意account/任意commandは禁止。全bounding/inheritable/ambient capabilityをdropしNoNewPrivilegesを保持、最終UID/GID/groups/5cap fieldを子が再確認する。他のsandbox/ReadWritePaths/5個LoadCredentialは従来値のまま。root前段のprivate sourceはappへ移さず、前段の秘密copy/DB/JMSはexec前にcloseし、成功execでroot JVM全heapを破棄する。Aの短期同OFDとsealed非秘密proof以外を意図的に継承しない。!前段もtrust boundaryの一部としてPT対象、まだ完成していないProduction Unitは現状の拒否mainを維持する。

| Directive | Web/API | 理由 |
|---|---|---|
| `Type` | `simple` | Java processを直接ExecStart、shellを挟まない |
| `User`/`Group` | service別専用account | OS権限分離 |
| `WorkingDirectory` | `/opt/schubert-nk/current/<web|api>` | release symlinkのread-only artifact |
| `EnvironmentFile` | `/etc/schubert-nk/<service>.env` | 非秘密・0600 root:service、古い環境を残さない |
| `LoadCredential` | DB/MQ/AES/HMAC secretを個別file | Secretをenv/argv/Gitへ出さない |
| `UMask` | `0027` | 新規fileのgroup以外読取禁止 |
| `Restart` | `on-failure`, `RestartSec=5s` | Process/protocol異常復旧 |
| Start limit | interval 600s, burst 5 | Poison/config errorのrestart loop停止。UI 252と一致 |
| `TimeoutStartSec` | 120s | readinessは別poll、起動hangのbound |
| `TimeoutStopSec` | Web 30s/API 60s | UI 251のgraceful上限 |
| `SendSIGKILL` | `no` | Timeout後の自動強制終了を禁止 |
| `LimitNOFILE` | 65536 | MQ/DB/media FD、leak監視 |

SSC-080/BUG-256/YKT-192: Web/APIの必須EnvironmentFileは各々`src/deployment/config/<service>.env.template`から固定1行`SCHUBERT_NK_CONFIG_DIR=/etc/schubert-nk`＋LFをrenderし、root:service0600で配布する。systemd managerが読み、serviceは値だけを起動前検査する。重複・未知/secret/alias・JVM option・placeholder・CRLFを含むfileは配布前拒否し、Java側も受領した値が固定rootと一致しなければ設定file読取前に停止。実root/manager配布はLinux ITで確認する。JVM optionは引続きUnit固定、秘密はLoadCredentialのみであり、envへ追加しない。

SSC-075: 起動前のOps Core management属性照会はSS321 §10の管理namespace限定一時reply Address/Queue権限を用い、各request 2秒で打ち切る。systemdの120秒上限を個々の無期限broker応答待ちの代用にしない。Ops credentialはWeb/API application roleへ流用せず、management一時Address/Queueの作成/削除失敗・close失敗はreadiness falseとして残す。

SSC-020: APIのUser/primary Groupはschubert-api専用を維持し、Transfer読取group schubert-webをSupplementaryGroupsへ追加する。Asset用のschubert-readと同様、共有対象は承認済みdataだけであり、Web/APIのcredentialやprivate runtime fileをgroup-readableへ変更しない。APIが作った新規日付directory/partに限り、保持inodeへgroup=schubert-webと0750/0640を明示設定して検証する。既存root/childの所有者・mode不一致は起動/処理失敗とし、applicationが修正しない。Provisioningと起動probeでgroup membership・新規作成権限を検証する。

SSC-079/BUG-253/YKT-191: Web/APIのreleaseとconfigはUI243/SS343の`root:schubert` directory0750・非秘密file0640なので、両unitの`SupplementaryGroups`へ`schubert`を明示し、OS accountの暗黙の補助groupに依存しない。APIは既存`schubert-read schubert-web`、Webは既存`schubert-read`を維持する。`schubert`は非秘密release/configの読取にだけ用い、`/etc/schubert-nk/credentials`のroot:root0700、private runtime、service別LoadCredentialの秘密権限は緩和しない。PTではmode/groupの独立固定oracleと両unitのdirectiveを照合し、実Linuxでのgroup provisioning/credential分離と起動後の実読取はIT開始条件へ残す。

### 4.3 Hardening

Web/API/batchは`NoNewPrivileges=true`、`PrivateTmp=true`、`PrivateDevices=true`、`ProtectSystem=strict`、
`ProtectHome=true`、`ProtectKernelTunables=true`、`ProtectKernelModules=true`、`ProtectControlGroups=true`、
`ProtectKernelLogs=true`、`ProtectClock=true`、`ProtectHostname=true`、`RestrictSUIDSGID=true`、`LockPersonality=true`、
`RestrictNamespaces=true`、`RestrictRealtime=true`、`RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6`を初期値とする。

- Web read-only: asset/transfer/current/config。Writeは`RuntimeDirectory=schubert-nk/web`とsystemd credential参照だけ。
- API read-only: asset/current/config。Writeはtransfer rootと`RuntimeDirectory=schubert-nk/api`。
- Batch write: backup/transfer/runtime。Credential/configはread-only。対象root以外の`ReadWritePaths`を与えない。
- Java JITを破壊する`MemoryDenyWriteExecute=true`は適用せず、他directiveとservice accountで防御。

`systemd-analyze verify`、`systemd-analyze security`、実機のroot/path権限負testをrelease gateにする。

### 4.4 Timer

`OnCalendar=*-*-* 05:00:00 Asia/Tokyo`、`AccuracySec=1min`、`RandomizedDelaySec=0`、`Persistent=false`。
Missした05:00をboot時に即実行してreboot loopを起こさない。Miss検出はmonitor/alertと手動`morning-run`で扱う。

## 5. Java/JVM・Spring process

### Private Inspector unit補足（SSC-049、PG-D-144）

`schubert-nk-inbox-inspector.service`はUser/Group=`schubert-inbox-inspector`の固定非root専用identity、Type=oneshot、Restart=no、SuccessExitStatus=10、TimeoutStartSec=30min/TimeoutStopSec=60s、KillMode=control-group/SendSIGKILL=no。ExecStartはrelease内の固定receipt wrapper、Java main直接起動を親の成功判定に使わない。DB/current2の必須LoadCredentialとprevious2の選択profileは343 §6.8。EnvironmentFileはroot所有静的設定とroot所有per-run2値だけ。Java option/classpath/commandをbatchが任意上書きする仕組みを作らない。

§4.3のNoNewPrivileges/PrivateTmp/PrivateDevices/ProtectSystem=strict/ProtectHome等の共通hardeningを維持し、asset/transfer/backupへのwriteを与えない。readonly release/configとprivate runtime credentialだけを利用しHTTP/JMS listenerを起動しない。After/RequiresはPostgreSQL、Beforeは通常Artemis/API/Web/Caddy、通常起動順を変えず親cleanupの内部で同期起動する。既に動いているAPI/Webを子unitが勝手に停止するConflictsは追加しない。親のinactive確認・OS lock・backup照合は別gate。

検査中は通常API/Web停止のため、その未使用枠内でInspector heap Xms128m/Xmx512m、Direct64m/Metaspace192m、ReservedCodeCache128m、MemoryMax1024Mを上限とする。UTF-8/UTC/ExitOnOutOfMemoryError/enable-native-access=ALL-UNNAMEDを固定し、heap dump自動出力は無効。実RSS/GC/timeout/TERM/権限配布は後続Linux IT。PTはmain・wrapperの全終了分岐、template/directive/profileの独立matrixとShellCheck/systemd-analyze検証を記録し、実unit起動成功と混同しない。

### 5.1 Resource

| Process | Heap | Direct/Metaspace上限 | systemd `MemoryMax` | Native headroom | Thread/pool |
|---|---:|---:|---:|---:|---|
| Web | `-Xms384m -Xmx768m` | 128m / 192m | 1536M | 448m | HTTP 16/max32、MQ wait 12/max20 |
| API | `-Xms512m -Xmx1024m` | 256m / 256m | 2048M | 512m | Sync consumer 4/max8、async 1、DB pool 8 |
| Batch | `-Xms256m -Xmx768m` | 128m / 192m | 1536M | 448m | DB connection 1、step worker 1 |
| Artemis | `-Xms768m -Xmx1024m` | 256m / 192m | 2048M | 576m | 321のbroker thread/config |

Web/API共通: `-Dfile.encoding=UTF-8`、`-Duser.timezone=UTC`、`-XX:+ExitOnOutOfMemoryError`、
`-XX:MaxDirectMemorySize=<table>`、`-XX:MaxMetaspaceSize=<table>`、`-XX:ReservedCodeCacheSize=128m`、
`-Xlog:gc*=info:stdout:time,uptime,level,tags`。Native headroomはcode cache 128m、thread stack、GC/JIT/JNI、NIO、launcher/OS allocationを含み、
同時最大時にも`MemoryMax`との差を0にしない。
Heap dump自動出力は無効のままとし、機密値を含むdumpを通常log rootへ作らない。

ITはRSS/heap/direct/metaspace/thread/GC pauseを実測し、上位16GB配分内だけで調整する。メモリ上限を広げる場合、
PostgreSQL/Artemis/OS/headroomの合計16GB以内を同時更新する。

SSC-019/021によりTransfer writer/Readerはshared storageのJava25公開FFM限定native portを使用する。Classpath起動のAPI/Web（storageを使用するbatchも）へ`--enable-native-access=ALL-UNNAMED`を明示し、JPMS化する場合は該当module名へ限定する。Native accessはOS権限分離の代替ではない。Linux/glibc・procfs self FD・必要attributeを共通readinessで、renameat2 no-replace・directory fsyncをwriterのreadinessで検証し、不成立時は起動成功としない。Systemdの既存hardeningを外さず、実機ITでWeb read-only/API限定writeのFD相対操作を確認する。

SSC-022の診断専用probeは333 §7.4へ従う。業務producer/HTTP開始前のexclusive startupで所有済診断fileだけを検査・清掃し、失敗/不確定公開/cleanup failureでreadinessを成功にしない。通常業務ready非削除、Web read-only、hardeningは維持する。

### 5.2 Spring主要値

| Key | Web | API |
|---|---|---|
| `server.address` | `127.0.0.1` | Main HTTP disabled |
| `server.port` | `8080` | `-1`相当 |
| `management.server.address/port` | `127.0.0.1:8081` | `127.0.0.1:8091` |
| Exposed actuator | `health,info,prometheus` | `health,info,prometheus` |
| Health details | loopbackでも`never`、component statusはlog/metric | 同じ |
| HTTP threads | 16 initial/max32、queue 32 | management最小 |
| Graceful shutdown | enabled、phase timeout 30s | enabled、phase timeout 60s |
| DB pool | Web technical max 2/min 1、connect 3s | max 8/min 2、connect 3s |
| JMS request wait | 2s、semaphore 12/max20 | Listener 4/max8、async 1 |

Actuatorはloopbackのみで、environment/configprops/heapdump/loggers/shutdownをexposeしない。`info`はrelease commit、
app/config/schema/protocol versionだけ。Secret/path/account/Queue bodyを出さない。

## 6. PostgreSQL 18

### 6.1 `postgresql.conf`初期値

| Key | Value | 理由 |
|---|---:|---|
| `listen_addresses` | `127.0.0.1,::1` | Loopback専用 |
| `port` | 5432 | UI default |
| `max_connections` | 40 | API 8＋Web 2＋batch/migration/ops＋管理・復旧余裕 |
| `shared_buffers` | 2GB | 16GB host/PG 4GB budgetの初期値 |
| `effective_cache_size` | 6GB | OS cacheを含むplanner hint、allocationではない |
| `work_mem` | 8MB | 同時sort/hashの倍率消費をbound |
| `maintenance_work_mem` | 512MB | Migration/index/maintenance、app同時多重なし |
| `max_worker_processes` | 8 | 小規模single host |
| `max_parallel_workers` | 4 | CPU/メモリ上限 |
| `max_parallel_workers_per_gather` | 2 | 1 queryの占有防止 |
| `temp_file_limit` | 2GB | 異常sortのSSD枯渇防止 |
| `wal_compression` | on | WAL容量抑制 |
| `min_wal_size` / `max_wal_size` | 1GB / 4GB | Checkpoint・30GB DB budget |
| `checkpoint_timeout` | 15min | 小規模の初期値 |
| `checkpoint_completion_target` | 0.9 | I/O平準化 |
| `deadlock_timeout` | 500ms | API lock timeoutと合わせ早期検出 |
| `password_encryption` | `scram-sha-256` | MD5非使用 |
| `ssl` | off | Loopback内のみ、OS・rolesで保護 |

`log_statement=none`、`log_parameter_max_length=0`、`log_parameter_max_length_on_error=0`とし、password/質問本文の
bind値をPostgreSQL logへ出さない。Connection/disconnection、checkpoint、lock wait/deadlock、autovacuum、
error severityは記録するが、slow queryの本文はapplicationのquery ID/duration metricで代替する。

### 6.2 Roleごとのtimeout

SSC-069/PG-D-187（2026-09-20）: §6.1の運用eventを`log_connections=on`、`log_disconnections=on`、`log_checkpoints=on`、`log_lock_waits=on`、`log_autovacuum_min_duration=0`で具体化する。slow SQL本文は`log_min_duration_statement=-1`、`log_min_duration_sample=-1`、`log_transaction_sample_rate=0`で無効にし、失敗SQL本文は`log_min_error_statement=panic`、DETAIL/HINT/QUERY/CONTEXTは`log_error_verbosity=terse`で抑止する。error severityは既定の記録を維持する。PostgreSQL自身のprimary error MESSAGEには不正入力値を含む場合があるため、これだけで任意入力の秘密非出力を保証しない。型付きbind/入力検証・実配備のOS log/redaction確認は別gateとし、raw DB logをPTエビデンスへコピーしない。

根拠: [PostgreSQL18 logging](https://www.postgresql.org/docs/18/runtime-config-logging.html)。配備雛形は`src/deployment/postgresql/`、全directiveとHBA16規則をPT-OPS-PGCFG-001～008で独立照合する。log保存先/rotationは配備環境とSS351で管理し、雛形だけで全運用完成としない。

`schubert_backup`行と後続hba entryはQA-043/UIC-003承認済みのrelease値である。

| Role | `statement_timeout` | `lock_timeout` | `idle_in_transaction_session_timeout` |
|---|---:|---:|---:|
| `schubert_app` | 1500ms | 500ms | 15s |
| `schubert_web_session` | 1500ms | 500ms | 15s |
| `schubert_batch` | 30min | 5s | 60s |
| `schubert_backup` | 30min | 5s | 60s |
| `schubert_migration` | 30min | 5s | 60s |
| `schubert_ops_ro` | 10s | 1s | 15s |
| `schubert_inbox_inspector`（SSC-049） | 30s | 5s | 専用単発transaction、process上限30min。既存provisioningに未設定のidle値を設定済みとしない |

Long-running migrationは個別migrationで`SET LOCAL`し、roleの無制限化をしない。

### 6.3 `pg_hba.conf`

```text
local  all          postgres                              peer
host   schubert_nk  schubert_app,schubert_web_session,schubert_batch,schubert_backup,schubert_ops_ro  127.0.0.1/32  scram-sha-256
host   schubert_nk  schubert_app,schubert_web_session,schubert_batch,schubert_backup,schubert_ops_ro  ::1/128       scram-sha-256
host   schubert_nk  schubert_migration                    127.0.0.1/32  scram-sha-256
host   schubert_nk  schubert_migration                    ::1/128       scram-sha-256
host   schubert_nk  schubert_inbox_inspector              127.0.0.1/32  scram-sha-256
host   all          all                                   0.0.0.0/0     reject
host   all          all                                   ::/0          reject
```

実際のhbaはroleごと1行へ分割してreview可能にする。`schubert_web_session`のhba接続を許しても、
331のgrantで業務schemaは不可。Remote CIDR、trust、password、md5を追加しない。

## 7. Artemis process・config

SSC103/PG321：`artemis.service`は実instance `/var/lib/schubert-nk/artemis`を専用`schubert-artemis`で起動する。`After/Requires=schubert-nk-cleanup.service`は必須であり、cleanup未配置を偽Unit/依存無視で補完しない。trusted root側がprivate regular0600の`/etc/schubert-nk/credentials/artemis-users`にJAAS hashed user propertiesを事前配置し、Unitは固定`LoadCredential`でprivate `/run/credentials/artemis.service/artemis-users`を受ける。vendorの`etc/artemis-users.properties`期待場所へはUnit private namespace内のread-only bindを使い、host既存fileを上書き/削除しない。秘密値・raw propertyをargv/env/log/Gitへ出さない。Unit構文・実効policy/credential bind・専用UID・起動/停止・journal cleanはそれぞれ独立判定し、loadedだけをbroker readinessやclean stopへ読み替えない。systemd bind適用順の実測に失敗すれば安全停止し別SSCで再判断する。

- `broker.xml`、Address/Queue/security/JMS値は321を正とする。Acceptors 61616/console 8161はloopbackだけ。
- Instance root `/var/lib/schubert-nk/artemis`は`schubert-artemis` 0700、journal/paging/large messageは別subdirectory。
- systemd `MemoryMax=2G`、JVM heap 1G/direct 256M/metaspace 192M、native headroom 576M、`LimitNOFILE=65536`、`Restart=on-failure`、start limit 5/600s、
  `TimeoutStartSec=120s`、`TimeoutStopSec=60s`、`SendSIGKILL=no`。
- `global-max-messages=50000`、`global-max-size=512MiB`、`max-disk-usage=90`、NIO File Journal、auto create/delete false。
  Address full/paging/page limitは321 §5.3のQA-042/UIC-002承認値を正とする。
- CredentialはJAAS/propertiesへhashとして格納、LoadCredentialから起動時にservice private runtimeへrender。
  Plain passwordを`broker.xml`、unit、argv、Gitへ置かない。

### 7.1 再配送確定値（QA-041/UIC-001）

`max-delivery-attempts=4`、`redelivery-delay=1000`、`redelivery-delay-multiplier=5.0`、
`max-redelivery-delay=30000`とし、実効delayを第1=1秒、第2=5秒、第3=25秒に固定する。Rendered `broker.xml`の
schema validationとIT時系列で321 §5.4との一致を確認する。

### 7.2 容量確定値（QA-042/UIC-002）

UI 231の合計保存上限をmemory＋disk pagingで実現する。321 §5.3に従い、`global-max-size=512MiB`、
Address memory high-water合計448MiB、`PAGE`、Address別page limit、page-full `FAIL`、disk-full `BLOCK`とする。
Rendered `broker.xml`はAddress別6組のbyte/件数上限、合計4.75GiB、page size 8MiB、read page 16MiB/100件を検証する。

## 8. Resource・disk合計・実測gates

| 分類 | 設計budget | Gate |
|---|---:|---|
| PostgreSQL | 4GB | RSS/shared/work memory合計、temp/WAL、query plan |
| Artemis | 2GB | JVM/direct/RSS、Queue 41,000件相当 |
| API | 2GB | 8 DB connection、8 sync consumer max、codec/file mode |
| Web | 1.5GB | 20 wait/20 stream、session/outbox |
| OS/Caddy/cache | 3GB | 停止/起動・broker I/Oを含む |
| Safety/DEBUG | 3.5GB | STANDARDでDEBUG 2GBを起動しない |

SSD 256GBはUI 253の45/35/30/10/5/10/80/5/36GB配分を維持。Filesystem 80% warning、90% critical。
`MemoryMax`とJVM heapを同値にせず、direct/metaspace/thread/native用余裕を残す。

ITはSTANDARD modeで10 concurrent user、20 media stream、Scenario file mode、backup/cleanupの個別・組合せを実測。
Upper limitの変更は実測証跡、合計budget、config manifest、354試験期待値を一括更新する。

## 9. Configuration validation・drift

| Component | Deploy前 | 起動後 |
|---|---|---|
| Caddy | fmt/adapt/validate、bind/cert/key permission | TLS/header/upstream/55160/firewall |
| Systemd | `systemd-analyze verify`、unit diff、user/path | `systemctl show`のMemoryMax/restart/timeout/hardening |
| PostgreSQL | config/hba parse、`postgres -C`、role/grant diff | `SHOW`実効値、pg_isready、remote接続拒否 |
| Artemis | XML schema、address/security diff | Management APIのAddress/Queue/journal/security/effective settings |
| Java | Java 25/toolchain、config schema、secret permission | `/info`のversion、health、JVM flag/resource |

実効値をsecret除外のcanonical JSONにしSHA-256をrelease/operation manifestへ保存。Driftは次回朝処理でwarning、
security/port/root/schema/protocolの差異はreadiness false。自動で未承認configへ書き戻さない。

## 10. 公式仕様参照

- [Caddy `reverse_proxy`](https://caddyserver.com/docs/caddyfile/directives/reverse_proxy)
- [Caddy `header`](https://caddyserver.com/docs/caddyfile/directives/header)
- [PostgreSQL 18 resource configuration](https://www.postgresql.org/docs/18/runtime-config-resource.html)
- [PostgreSQL 18 connections and authentication](https://www.postgresql.org/docs/18/runtime-config-connection.html)
- [Artemis Address Settings](https://artemis.apache.org/components/artemis/documentation/latest/address-settings.html)

Minor/patch導入時は必ず導入versionの公式資料とconfig validatorで再確認する。QA-042/UIC-002承認設定のArtemisは
`page-limit-*`とAddress別`disk-full-policy`を両方備える2.50.0以上を起動前gateとする。

## 11. SS設計判断

| ID | 判断 | 根拠・理由 | 後続影響 |
|---|---|---|---|
| SS-D-036 | Web/API management portを8081/8091に分け、API main HTTPを無効化 | UI 211の非公開Actuator、APIのBrowser直接応答禁止を強制 | Port/firewall/readiness IT |
| SS-D-037 | PostgreSQL初期値をshared buffers 2GB、max connections 40、role別timeoutに固定 | 16GB hostでwork memoryの乗算増加とpool上限をbound | Query plan/負荷実測で調整証跡 |
| SS-D-038 | Java OOM時はprocess exit、heap dump自動生成なし、systemdは5回/10分でrestart抑止 | UI 252の値で、復旧と機密保護、restart loop防止を両立 | OOM/limit IT、runbook、metric |

## 12. 禁止事項

- Caddy以外のportをglobal/LAN bind、Artemis console/Actuator/PostgreSQLをfirewall例外公開。
- Secretのunit `Environment=`/argv・Caddyfile/broker.xml/application YAML/Gitへの平文格納。
- Systemdを迂回した`java -jar`・broker・batchの手動常用起動。Stop timeout時の自動SIGKILL。
- PostgreSQLの`trust`/MD5認証、remote hba、application superuser、Webへの業務schema grant。
- Artemis redeliveryをQA-041/UIC-001承認値の1秒、5秒、25秒以外でrelease確定すること。
- UIの用途別合計保存上限を`max-size-bytes`へ直接転記すること、全Address `BLOCK`へ戻すこと、QA-042承認値を無断変更すること。
- `schubert_batch`へdump対象tableのSELECTを与えること、`schubert_backup`へDML/DDL/SET ROLE/復号keyを与えること。

## 13. 更新履歴

| 日付 | 内容 |
|---|---|
| 2026-08-31 | Caddy/systemd/JVM/PostgreSQL/Artemisの初期値、hardening、validationを作成。 |
| 2026-08-31 | 横断監査でPostgreSQL role名をUI 212の`schubert_*`に統一。 |
| 2026-08-31 | 横断監査でCSPをnonceなし・same-origin外部asset方式へ統一。 |
| 2026-08-31 | 横断監査でWeb DB poolをUI 212の上限2へ修正し、Artemis容量設定をQA-042/UIC-002保留として追加。 |
| 2026-08-31 | `pg_dump`用の`schubert_backup` role候補をtimeout/`pg_hba.conf`へ反映し、QA-043/UIC-003回答待ちとした。 |
| 2026-08-31 | 横断監査でJVMのheap/direct/metaspace合計がMemoryMaxへ達していた値を是正し、process別native headroomを確保。 |
| 2026-09-01 | QA-041/UIC-001承認を反映し、Artemis再配送設定と実効delayを1秒、5秒、25秒へ確定。 |
| 2026-09-01 | QA-042/UIC-002承認を反映し、Artemisのmemory high-water、disk paging、page/disk full設定をrelease値へ確定。 |
| 2026-09-01 | QA-043/UIC-003承認を反映し、`schubert_backup`のtimeout/hbaとbatchとの権限分離をrelease値へ確定。 |
