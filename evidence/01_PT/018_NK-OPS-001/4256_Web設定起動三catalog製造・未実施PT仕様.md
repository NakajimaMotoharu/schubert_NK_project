# Web設定起動三catalog製造・未実施PT仕様

NK-OPS-001/WBS-P018-06/BUG-2801/YKT2359/SS342343SSC301/351451。WebProcessMain設定callback二口とWebRuntimeExecution Lifecycle一口へ既知例外の固定化前fatalgraph確認を追加。通常70/50、checkedIO分類、純env IAE、所有slot、Root認可、UNKNOWNframe保持/stop-close優先は不変更。原source全byte逆変換・GJF/CS0をPG29076で確認。

独立期待値：cause/suppressed/cycle/SQLnextにErrorがあれば同一identityがslot70更新より先に伝わる。Errorなし既知IAE/NSAは70、Lifecycleは固定IOExceptionで秘密causeなし。既checkedIOの経路は従来通り。失敗close未確認ではexactframeを保持し後続所有を解放しない。期待値は固定設計/既catalog契約から作成し、production methodで生成しない。

Main compile/NullAway/fullstatic/wholePT/coverageはNOT-RUN。既wholeTestsはactualRoot/HTTP/actual4を含むため資格不成立範囲はHOLDを維持し、method部分抽出や偽Root fixtureで代替しない。source修正を実行成功と呼ばずBUG-2801 OPEN。実Root/VM/HTTP/DB/JMS/native/actual4.class/cache/compile/load/init全0。PG29076は公開source inverse/GJF/CSだけのmetadata終了0で、製品PT PASSではない。


source固定commit 631fa26b708ddeb5d5c60b11f33786a0ee326a8b、独立sourcejoin [manifest](../018_NK-OPS-001/evidence/PG29080-web-two-main-source-join-v1/manifest.json) SHAa18ec50afc39e3f9e07f1023e33f630933a20a48143fece1952064098491c1f7。BUG2801 WebProcessMain設定callback二口/WebRuntimeExecution Lifecycle一口へ既知catalog fatalgraph guardを固定化/slot70更新より先に追加。原2Main全byte逆変換/GJF-CS0、pureENVconstructorIAE/checkedIO50/通常70/UNKNOWNexactframe保持・stop/close優先/Root認可順は不変更。Main compile/NullAway/fullstatic/PT/coverageは未実施、actual4.class/cache/load/init/Root/VM/HTTP/backend/native0。BUG2801はOPEN、同じsource全体へ旧component成功を移植せず、通常16成功は元run/source限定で維持。 製品PT0、runtime/coverage未受入。
