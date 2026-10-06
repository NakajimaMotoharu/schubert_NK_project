# PG478真正保守・独立削除oracle仕様

NK-OPS-001/NK-BAT-001/NK-DAT-001、OPS009/DAT009/FIL006、UI232/234/235/236/251、SS324/331/332/341/343/352/355、SSC191192196/QA047/PG-D385。Production/full source cce61f63900b1479f9f8dbdc338e222b1c8c38a3、実release PG477、実経路run PG478を区別。工具をProductionPTへ加算しない。

| Test ID | 対象と独立期待値 |
|---|---|
| PG478-DEP008 | 全24table全列を独立SQL/readonly repeatable-read2回で固定。command0/32MiB上下境界9反例。Root700/0600だけ保存、raw/key/session/Git0。旧8MiB拒否を分離。 |
| PG478-DEP009 | SS331/332/UI251の保持式をPython UTC selectorへ手書きし、DDL固有PK/nonempty fixture/24h/168h/90d/400d/保護FK/null/境界20検査。actualcutoffは保存lower/upper内、集合は窓内不変であることを確認。production maintenance function/expected生成0。 |
| PG478-DEP010 | expired Inbox7のNONE query応答は独立Python AES-GCM/zlibで復号し、SS352 length-prefix AAD＋UI232 header/234235236 DATA-record offset/型/NFC/padding/count・completed millisecond/相関/owner/token/ref/最低24hを検査。過去query結果を現在DBへ再検索しない。NIST固定AES256 tag・手書き576byte UDTRSP error vector/AAD/byte変造29検査。暗号・wire平文は通常log/Git0。 |
| PG478-DEP011 | 旧Backup直下6（part/未知を含む）＋新1≤7なので世代削除0。旧全20entryのbyte/identityを保存。Transfer5の正規YYYYMMdd empty dirだけSS341通り削除、root同inode/unknown削除0。全旧原本/旧64startup/27nativeactualは保全、正規新原本/新4launch/epochは別allowlist。 |
| PG478-NATIVE001 | 新owner normal受入後、new Root400 observerを先行、一回外部Morning（O_EXCL guard）。正規new-run→真正同owner Backup/Inspector/cleanup/Expiry→同Root普通API所有保持Web/Caddy/A01→元30min DONE/保持原本/全後条件→ownedTERM/nativefresh same-source。API readyだけを親成功へ算入0、旧SUCCESS skipへInspector追加0。 |

実行: python3 -B tools/quality/vm/050_s1/pg478_{preflight,cleanup_oracle,inbox_oracle,source_binding}_test.py、pg478_preflight_host.py（v2済・再発行禁止）、Root pg478-oracle-tools-v2/pg478_inbox_oracle.py capture（済・再発行禁止）、pg478_prepare_observer_v1.py（済）、bash pg478_parent_observer_v1.sh→python3 -B pg478_external_start_once.py cce61f63900b1479f9f8dbdc338e222b1c8c38a3 613b71a06c2b215887219cd3502d3db34542fea957e0d88dbb9c54c8bab18667（一回だけ・発行後再付着）。private WorkPG379/Root pg478-newrun-preflight-v2。実HTTP/SQL/Unit/journal/PID/Invocation/cutoff/終了code・全四coverage/native/static6は同sourceの結果を381へ追記。IT/ST合格0。
