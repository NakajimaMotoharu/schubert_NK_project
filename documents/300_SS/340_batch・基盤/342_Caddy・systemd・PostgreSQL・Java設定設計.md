# Caddy・systemd・PostgreSQL・Java設定設計

## 1. 目的・状態

Caddy、systemd、PostgreSQL、Artemis、Web/API/batch Java processの初期実効値、入力file、port、resource上限、
hardening、timeout/readinessと検証方法を定める。

- 状態: `確認待ち`。本書のArtemis再配送第3間隔のみQA-041/UIC-001待ち。その他は確定。
- 上位設計: UI 211～212、231、251～253
- 関連RD: SYS-002～SYS-004、SYS-012～SYS-014、OPS-001～OPS-012、MON-001～MON-013、
  PER-001～PER-010、AVL-001～AVL-010
- 関連QA/RDF/UIC: QA-007、QA-010～QA-011、QA-016、QA-021～QA-022、QA-027、QA-029、QA-041、RDFなし、UIC-001
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
- CSPはnonceを持つapplication responseごとにWebが設定し、Caddyで静的CSPへ上書きしない。
- Access logはJSON、path/status/duration/bytes/remote IP/request IDだけ。Cookie、Authorization、query string、request/response bodyを
  filter除外する。Filter非対応の導入minorではaccess logを最小化し、Web WLGEVT01を業務監査正本とする。

### 3.2 TLS・検証

- QA-022に従い初期はCaddy internal CA/IP certificate。警告を許容するがHTTPへdowngradeしない。
- Private keyはCaddy専用state/credential、root/Caddyのみ読取。Fingerprint、有効期限、検証手順をconfig manifestへ記録。
- Domain/公的証明書移行時はsite address/TLSだけ変更。`tls_insecure_skip_verify`はupstream/clientとも使わない。
- Deploy前に`caddy fmt --diff`、`caddy adapt --validate`、`caddy validate`、起動後TLS/header/loopback upstreamを試験。

## 4. Systemd dependency・unit設定

### 4.1 Dependency

| Unit | `After` | `Requires` | `Wants`/note |
|---|---|---|---|
| `schubert-nk-backup` | PostgreSQL | PostgreSQL | 失敗はmorning続行 |
| `schubert-nk-cleanup` | backup | PostgreSQL | Backup成否はDB rowで分岐 |
| `artemis` | cleanup | cleanup | Cleanup safety failureで起動不可 |
| `expiry-cleanup` | Artemis | Artemis | API Consumer前に実行 |
| `schubert-nk-api` | expiry, Artemis, PostgreSQL | Artemis, PostgreSQL, expiry | readiness poll後にWeb |
| `schubert-nk-web` | API, Artemis, PostgreSQL | API, Artemis, PostgreSQL | technical DBが必要 |
| `caddy` | Web | Web | Packageの自由先行起動をdisable |

`schubert-nk-morning.target`が全unitをWantsし、通常bootの`multi-user.target`からWantsする。BackupのFAILEDは
target全体を止めず、cleanupが削除skipを記録した上で後続する。

### 4.2 Java service共通

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

### 5.1 Resource

| Process | Heap | Direct/Metaspace | systemd `MemoryMax` | Thread/pool |
|---|---:|---:|---:|---|
| Web | `-Xms512m -Xmx1024m` | Direct 256m, Metaspace 256m | 1536M | HTTP 16/max32、MQ wait 12/max20 |
| API | `-Xms768m -Xmx1536m` | Direct 256m, Metaspace 256m | 2048M | Sync consumer 4/max8、async 1、DB pool 8 |
| Batch | `-Xms256m -Xmx1024m` | Direct 128m, Metaspace 256m | 1536M | DB connection 1、step worker 1 |
| Artemis | `-Xms1024m -Xmx1024m` | Direct 512m | 2048M | 321のbroker thread/config |

Web/API共通: `-Dfile.encoding=UTF-8`、`-Duser.timezone=UTC`、`-XX:+ExitOnOutOfMemoryError`、
`-XX:MaxDirectMemorySize=<table>`、`-XX:MaxMetaspaceSize=256m`、`-Xlog:gc*=info:stdout:time,uptime,level,tags`。
Heap dump自動出力は無効のままとし、機密値を含むdumpを通常log rootへ作らない。

ITはRSS/heap/direct/metaspace/thread/GC pauseを実測し、上位16GB配分内だけで調整する。メモリ上限を広げる場合、
PostgreSQL/Artemis/OS/headroomの合計16GB以内を同時更新する。

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
| DB pool | Web technical max 4/min 1、connect 3s | max 8/min 2、connect 3s |
| JMS request wait | 2s、semaphore 12/max20 | Listener 4/max8、async 1 |

Actuatorはloopbackのみで、environment/configprops/heapdump/loggers/shutdownをexposeしない。`info`はrelease commit、
app/config/schema/protocol versionだけ。Secret/path/account/Queue bodyを出さない。

## 6. PostgreSQL 18

### 6.1 `postgresql.conf`初期値

| Key | Value | 理由 |
|---|---:|---|
| `listen_addresses` | `127.0.0.1,::1` | Loopback専用 |
| `port` | 5432 | UI default |
| `max_connections` | 40 | API 8＋Web 4＋batch/migration/ops＋余裕 |
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

| Role | `statement_timeout` | `lock_timeout` | `idle_in_transaction_session_timeout` |
|---|---:|---:|---:|
| `nk_api` | 1500ms | 500ms | 15s |
| `nk_web` | 1500ms | 500ms | 15s |
| `nk_batch` | 30min | 5s | 60s |
| `nk_migration` | 30min | 5s | 60s |
| `nk_ops_ro` | 10s | 1s | 15s |

Long-running migrationは個別migrationで`SET LOCAL`し、roleの無制限化をしない。

### 6.3 `pg_hba.conf`

```text
local  all          postgres                              peer
host   schubert_nk  nk_api,nk_web,nk_batch,nk_ops_ro     127.0.0.1/32  scram-sha-256
host   schubert_nk  nk_api,nk_web,nk_batch,nk_ops_ro     ::1/128       scram-sha-256
host   schubert_nk  nk_migration                          127.0.0.1/32  scram-sha-256
host   schubert_nk  nk_migration                          ::1/128       scram-sha-256
host   all          all                                   0.0.0.0/0     reject
host   all          all                                   ::/0          reject
```

実際のhbaはroleごと1行へ分割してreview可能にする。`nk_web`のhba接続を許しても、
331のgrantで業務schemaは不可。Remote CIDR、trust、password、md5を追加しない。

## 7. Artemis process・config

- `broker.xml`、Address/Queue/security/JMS値は321を正とする。Acceptors 61616/console 8161はloopbackだけ。
- Instance root `/var/lib/schubert-nk/artemis`は`schubert-artemis` 0700、journal/paging/large messageは別subdirectory。
- systemd `MemoryMax=2G`、JVM heap 1G/direct 512M、`LimitNOFILE=65536`、`Restart=on-failure`、start limit 5/600s、
  `TimeoutStartSec=120s`、`TimeoutStopSec=60s`、`SendSIGKILL=no`。
- `global-max-size=1GiB`、`global-max-messages=50000`、`max-disk-usage=90`、NIO File Journal、auto create/delete false。
- CredentialはJAAS/propertiesへhashとして格納、LoadCredentialから起動時にservice private runtimeへrender。
  Plain passwordを`broker.xml`、unit、argv、Gitへ置かない。

### 7.1 QA-041保留値

`max-delivery-attempts=4`、第1=1秒・第2=5秒は確定。第3はUI 231の30秒とArtemis標準倍率式の25秒のいずれかが
QA-041回答まで未確定である。回答前にrendered `broker.xml`の当該値をrelease確定しない。

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

Minor/patch導入時は必ず導入versionの公式資料とconfig validatorで再確認する。

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
- QA-041未解決のままArtemis redelivery第3期待値をrelease確定すること。

## 13. 更新履歴

| 日付 | 内容 |
|---|---|
| 2026-08-31 | Caddy/systemd/JVM/PostgreSQL/Artemisの初期値、hardening、validationを作成。 |
