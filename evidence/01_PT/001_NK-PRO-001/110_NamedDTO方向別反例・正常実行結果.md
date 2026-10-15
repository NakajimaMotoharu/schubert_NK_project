# Named DTO方向別反例・正常実行結果

2026-10-15、109の実診断結果。Production a9/PG2802変更0。

before-v3/285b40e21の正常二成功＋相互swap/安定誤byteの実二見逃しを保持。修正前BUG1288は48e4dd275、BUG1285はd19ec4b5aで起票済み。d45aec8f135f864030b5ca916f7ee973ada1c106で新allNamedTypesHaveIndependentDirectionalFieldMeaning一method・Test-only helper・手書き135 accessor fixture、既P09固定384byte oracleを追加した。Main/resource/pom/署名/配備/VMを変更0。

after-v3/exec90848 actual0、09:06:21.435730～09:06:29.178603Z、payload SHA59ccf442032b2a90c40a56629acff71f4c42df3b6f4eb06ea5dbfd6445f4367c。

| case | 実selector／期待 | 実結果 |
|---|---|---|
| NORMAL_TYPE | 新allNamedTypesHaveIndependentDirectionalFieldMeaning | 一JUnit実成功、69型/295component/79任意/4空/135binding/全参照constructor null・全from null・redactionを独立照合 |
| DTO_RECIPROCAL_SWAP | 同selector、元beforeと同じUsername/Password双方向swap | 一JUnit AssertionFailedError、actual1で正しく拒否 |
| NORMAL_CONCURRENT | sharedCodecProducesIdenticalBytesUnderConcurrentUse、独立384byte | 一JUnit実成功、8worker全future一致 |
| STABLE_WRONG_BYTES | 同selector、元beforeと同じstable誤byte | 一JUnit AssertionFailedError、actual1で正しく拒否 |

元工具1286/1287のv1/v2は未JUnitの失敗として別保全し、新v3に改名/合算0。純四・実JDK25.0.4/java.home・engine同version launcher/全realpath/hash資格、全4caseのcompiler warnings0、元Jar/lib同hash/agentexec生成0まで実証済み。BUG1286/YKT1052・BUG1287/YKT1053の有限工具scopeは全対象修正又は非該当根拠・再発防止・実再試験が揃う。Production PT/coverage/全PGPT認定ではない。

公開の実source/UTC/selector/終了code/hashは`evidence/provisional/PG3294-directional-oracle/manifest.json`。元compile/testログと完全classpath/lib/入力は私有に保持する。実credential、password、token、session、鍵は使用/出力0、値は合成fixtureだけ。

次の関連実行はPG3298固定clean source、`PYTHONPATH=tools/quality:tools/quality/vm/050_s1:<pyflakes-runtime> python3 -B tools/quality/pg3298_directional_protocol_regression.py`。Protocol85/17suite/174Main、元a9全Jar member同byte・全四100/静的0/FES-flaky-notrun0を期待。原実終了/source/hash後のみpg3300_directional_protocol_independent.pyで全原XML/同archive全input/同counter/static/全memberを別RO照合。未実行・途中結果は合格へ含めない。

当related後、必要一全体3702/542/1643＋別独立＋同native28の全byte/CRC資格を閉じるまで、BUG1285/1288/YKT1051/1054は未完、P001-03/P002-02は未認定。旧3701/84と新85を加算せず、旧source/runの正式1964/53・工数null/QA051final保留を維持する。
