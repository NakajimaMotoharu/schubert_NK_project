# NK-OPS-001 固定native採取profile・同source集計結果

2026-10-06 JST、暫定限定・正式未認定。結果と対象byteは各safe manifestを正とする。

- `PG469-child-native-counter-v1/manifest.json`：actual session34911 exit0、SHA292df86ec01a0b2cfc1e7e8da6dcbbfa6337ca7d2745a3ae63e91deb6435de94。同D3 frozen6/親子4本各1session/NoMatch0。Batch未網羅B1239→989/L3660→1728/M597→303/C39→14、Bootstrap B53→45/L34→16/M16→9/C0。API B101/L190/M11、Web B57/L189/M26は未解消、Protocol/Storage全miss0。rootAPI0byteをoldexecへ置換0、全100%未達。
- `PG470-profile-selected-v4/manifest.json`：session18796 exit0、02:56:27～02:57:01、47PT/6suite/FES0、静的3module0/NullAway/Werror/format。SHAeeae17a05e563f3a2f1ea0a8651177e292b2e9fb9f28737f66db7c5cc992416f。profile/argv/entry source6fileの当dirty hashを保存、別D3 nativeへ合流0。
- v1 upstream no-tests exit1/not-run、v2 profile/control34PT成功だがnamed-entryなし、v3旧regular0640のumask mismatch1F/actual1。BUG751/YKT531を修正前登録→固定wrapper子0027のv4で全12 private-entry suiteを独立再試験。Production/期待値変更0。collector初稿はwhole-second終了markerとnanosecond mtimeを誤比較してexit1/nooutput、量子化区間を明示した修正稿actual0のみ採用。
- manager Invocation引数展開probeは独立transient one-shot actual0、Root pg469-invocation-env-v1のsafe結果/私有原記録を保持、app start/stop0。同Unit`${INVOCATION_ID}`==actual環境、UID999、UnitGC/not-found/PID0/control0/job空。実API/Web新profile配備への代用0。

全private原本/Backup/旧exec/heap/credential/PG442pause/stash7/Scenario3/Currentを保持。正式PT-WEB-20260925-24/1964PT/53scope/48.3%不変更、coverage100/全CHR/PGPT/ITSTの合格宣言0。Root ordinary本体・公開agent export・new-only全後条件は未実装/未検証のまま、通常限定成功で停止せず継続。
