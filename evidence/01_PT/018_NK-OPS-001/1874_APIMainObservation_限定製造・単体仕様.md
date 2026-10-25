# API Main監視assembly供給・限定製造/単体仕様

2026-10-25/WBS-P018-05/group2106/PG-D639、P018-09参照追加費0。開始1/2/3pp/cap3、fresh58残42/reset1793382075。元共有0/reset1793306748・90上限/捕捉下限83・不明2/正確null、80大型抑制を維持。当cap3＋保全buffer2は90内へ収まる確認（bufferは実費補填ではない）。一つの同API接続経路の短工程、元/v4/v5/群開始値は固定。

Program NK-OPS-001/class ApiProcessMain prepareObservations/closeObservations/既startNativeのassembly接続、SYS-002/004/RD171/UI252/SS311342343351、1871/1873/1869。保持済みobservation owner→initialize→管理serverはborrowed metrics→管理終了後observation closeを既ResourceScopeへ接続。factoryはborrowed Pool・Life remaining/failure・固定UNKNOWN policyを取得前準備。closeは既ResourceScopeの既所有object release frameでLife.stop→observation.close、stop失敗でもreleaseを通し、native UNKNOWNでは同frame保持。再acquire/新deadline/Pool ownership移転ではない。Unit/親の実停止/Outbox無期限joinは別未受入HOLD。

新ApiProcessObservationFactoryTestは静的二入口だけを呼び、ApiProcessMain object/main/run/admission・startup file・hook登録・TERM・Hikari pool起動・実DB/VM/Root/配備は0。default Main constructorを持つ旧Testを選択せず、新8classだけ。STD initializeは詳細SQL/bean/worker未読、DEBUGは未初期化又は不正型fixtureでworker開始前まで。実producer/ordinary API ready/ownedstop/CHR/nativeの代用にしない。

| Test ID末尾（APIOBSBOOT） | 入力/操作 | 独立期待/fixture |
|---|---|---|
| 001 | mode/pool/Life null | NPE、Pool操作0/停止なし |
| 002 | 空/小文字/未知mode | IAE、Pool操作0/停止なし |
| 003 | STD prepare/init/render/正規release | 詳細outboxなし・bindings空・Life.stop/残60e9、context停止済み |
| 004 | DEBUG prepareだけ→release | Clock/Pool未読、未起動workerで元remaining不要、Life初回clock一 |
| 005 | close両null境界 | NPE・停止/clock0、既ownerはまだ初期化可 |
| 006 | first close100→109再close | 期限renew0・clock初回一/残59_999_999_991 |
| 007 | stop clock Error/STD既知no-worker | 同fatal保持、既ResourceScopeでcontext close済み・残0、Pool操作0 |
| 008 | DEBUGに不正型DataSource | SDK setup ClassCast前提違反、worker start/SQL0、保持済みownerをreleaseで回収 |

期待はliteral/mode出力/同identity/独立回数、productionでexpected算出0。Pool proxyは全methodに失敗を返してProvider操作0を強制。fixtureのmanual closeはmanual local/try-finallyで管理しTWR direct close警告を作らない。

normal六→新8普通PT→当source全Main unitの実coverage（interface metadataも存在どおり）/三static→Module/旧byte/owner/trace→1875へ。実Main未実行ならmissed/未分類を保存し全四100/Program PT/451完了にしない。原成功4222/44/26/18/10の確認再演0・新sourceへの転用0、正式1964-53/原190新受入0/QA051final・工数null/全actualHOLD保持。普通保存で止めず、元90/実残10等の既条件まで短い許可工程を継続する。
