# NK-OPS-001 静的Inspector環境file実行結果

011/PT-OPS-CFG-001～006、PG-D-151。探索2（2026-09-12 20:58:50 JST）でStorage50/Batch71計121件、4coverage100%・静的解析成功。render雛形もliteral expectedへ完全一致。BUG147/YKT115は先行a98ac3cb後にcollector件数の二重管理を修正し、017の1件/019の16件canary成功。正式PT-WEB-20260912-01の全体試験・35scope同時点性検証前であり、新6件はまだ正式認定しない。保持inode/属性・bounded read・atomic publish・親結線は別の未完了条件。
