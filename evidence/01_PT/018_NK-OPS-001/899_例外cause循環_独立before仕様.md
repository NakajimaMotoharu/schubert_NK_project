# PT-OPS-CAUSE3404-001 独立before仕様

対象WBS-P006-02、OutboxJmsSender.isDuplicateConfirmation/send。RD MQ-006/008、UI242、SS324§8、411§5、451、BUG1299/YKT1065。PG3404、Production a9/PG2802、実行前HEAD2820fafc6。上位仕様・Current baseline不変更。

原PG3372の真正Maven0/3706を読取認証し、そのAPI実Jarと同runの他五Main Jar・元JUnit依存Jarだけを使用する。独立同package Java mainを別new-only private slotでJava25 `--release 25 -Xlint:all -Werror` compileし、実package契約を通常呼出しする。private reflection・Production/Main書換え・稼働PG3398 source変更・Broker/DB/VM操作なし。

| case | fixture/input | 独立期待値・根拠 |
|---|---|---|
| acyclic | 非duplicate Runtime cause二段 | 有限false：typed broker duplicateなし |
| direct | ActiveMQDuplicateIdException実型 | 有限true：当型による確定duplicate |
| cause-cycle | 標準Runtime A.cause=B/B.cause=A | 有限false：合法cycle、duplicateなし |
| mixed-cycle | 標準JMS.linked=B/B.cause=JMS | 有限false：異edge cycle、duplicateなし |
| alternate-edge | JMS.linked=通常B/JMS.cause=typed duplicate | 有限true：cause側に実型が到達可能 |
| reachable-through-cycle | linked/cause循環＋別causeにtyped duplicate | 有限true：cycleにより確定型を見落とさない |
| suppressed-only | root.suppressed=typed duplicate | 有限false：rollback等の二次失敗をcommit確認へ昇格しない |
| message-only | duplicateらしい固定synthetic文字列のみ | 有限false：message文字列は確定根拠ではない |

期待値はfixture graphの型とedgeを明示したliteralであり、Production methodから生成しない。初期のcause/link自己循環既Testは保存し、二nodeとの違いを確認する。個々のforked JVMはENTERの即時flushを必須とし、3秒未帰還は親の所有ProcessへTERM/5秒wait/reap、終了143は**負系canaryの回収であって正常Production成功ではない**。TERM不能時だけ自分のchildをkillして工具を失敗終了する。8子の全回収を確認し、他PIDを操作しない。元DB・鍵・session・token・利用者dataなし、出力は固定marker/hashだけ。

実行command=`PYTHONPATH=tools/quality python3 -B tools/quality/pg3404_outbox_cause_before.py`（new-only一回、失敗slot上書き禁止）。工具0は予測した障害再現と子回収の成功を示し、Production合格や新JUnit件数へ加算しない。全体3707は元job53556から別に回収する。当beforeのcoverageは非適用（隔離診断、正式Main counterを増減しない）。後続是正では正常/異常/null・cycle/DAG・rollback/closeのJUnit、全YKT対象の根拠と再発防止、必要新source品質を別記録する。

実行結果・OS/JDK・元Jar/class/source/manifest hash・終了code/期待/実際/所有回収は `evidence/provisional/PG3404-outbox-cause-before/manifest.json` と私有 `pg3404-outbox-cause-before-v1` に保存する。正式1964/53、個別17/190、工数null、QA051final保留は不変更。
