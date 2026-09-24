# NK-OPS-001 Expiryマイクロ秒境界 PT実行結果

PG248/BUG-239。2026-09-24 15:07 JSTの修正前TDD REDは選択6件中2 failure/exit1（PT-OPS-MQ-026実Brokerの期待対象1/実0、PT-OPS-MQ-028固定閾値期待`1789603200001`/実`1789603200000`）。不合格を合格数へ算入しない。15:08 JSTの修正後選択は6/6、failure/error/skipped0、実Broker同時刻保持/+500µs観測1/+1ms削除1、固定正/負epoch selectorを確認した。Batch `clean verify`は15:15 JSTに全397PT、failure/error/skipped0、JaCoCo全check達成・Production SpotBugs0、対象class instruction318/318・branch44/44・line62/62・method8/8・class1/1。019負canary99/99。source固定commit・全reactor/49scope/hash前のため**PG248は未認定**。

正式対象commit/branch、日時/OS/JDK/Artemis/tool、command/exit、Test ID別入力・独立期待・実際、coverage/static、関連BUG、証跡path/hashは後続同一source正式runで追記する。親DB stage/terminal commit・same-run/health/criticalは引き続き未完了。
