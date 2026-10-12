# 684 NK-OPS-001 Root世代・二読race（限定PT）

対象：RootStartupContext.observeService/recheckServiceGeneration/serviceGenerationExited、関連OPS009／UI251／SS343353354／451、WBS-P018-03.02。独立literal kernel/systemd fixtureを使用し実ownerを授与しない。開始event0510、凍結subset見積0.25/0.5/1.5pp、個別実費/N/Tはnull。class=RootGenerationCounterexampleTest。

| Test ID（method rootgen1741末尾） | 入力・独立期待値 | 結果 |
|---|---|---|
| ROOTGEN-1741-001 | API/Web literal世代は有効、UID drift後の新Root捕捉は拒否 | PASS |
| ROOTGEN-1741-002 | 異service/boot/init/parentPID/group snapshot、procアクセス前IOException | PASS |
| ROOTGEN-1741-003 | recheck boot/init/startticks/service/parent不一致拒否 | PASS |
| ROOTGEN-1741-004 | 存在→消失はfalse、消失→存在は拒否、PID二読厳密 | PASS |
| ROOTGEN-1741-005 | 親再照合後三回目UID/procfs/initexe/boot/PID1変化、targetUnit未読取で拒否 | PASS |
| ROOTGEN-1741-006 | pid1/zeroInvocation/変動ticks拒否 | PASS |
| ROOTGEN-1741-007 | APIへ保守期限/Morningへservice期限のrole借用拒否 | PASS |
| ROOTGEN-1741-008 | kernel status DEL127 byte拒否 | PASS |

Main2741c4546afad6c1e8b6efbd53dfb58144edf7bb、最終Testsource665550fac2a094643106781944636ce8f38e1dc3。LAN Ubuntu26.04/x86_64/JDK25.0.4/Jupiter5.13.4/Platform1.13.4/JaCoCo0.8.15、fixture/Main6JARをpinし専用classes/XML/exec。実行command=`PYTHONPATH=tools/quality:tools/quality/vm/050_s1:<fixed pyflakes> python3 -B tools/quality/pg1743_root_generation_boundaries_selected.py`、actual0/exact8/FES-aborted-notrun0/Werror0/MainCRC0/元fixture不変/VM-DB-Unit操作0。

初回1741の4件は履歴（SHA89a47edb…）、最終8へ加算0。1743 serverSHA7b8d2bd15ad3aedef365ecf0b4793539e03793a0903107a92798859807dec06e。旧1744資格はhost件数guard誤継承で転送前停止、未資格/空dirのまま保全（BUG1159/YKT927）。新版1745の明示8 oracleはactual生成定義のunique/missing/count/failed/skipped/unknown反例を独立実施し成功、read-only XML/source/JAR/library/fixture/exec/counter資格0、SHAacaa8faa41a41efe9b9cfe4dab4e226d74c0854ad30c1132adf8f53aab4d2360。試験再実行0。

当Main6host/current9native/API5/Backup7/当Root8の残870L/169M/9C/686B、直前705Bから19B減。四100未達、fresh全3612未実行。正式1964PT/53scope/wholeleafdelta0/工数率null不変。private WorkPG379/pg1743-root-generation-boundaries-selected-v1・pg1745-root-exact-qualified-v1、LAN PG1743-selected-v1/PG1745-selected-qualification-v1。公開manifest=684_manifest.json、秘密raw/原本/DB実体なし。

子02終了依存：子01 whole原本世代/所有資格、全missing/corrupt/revoked/foreign FD matrix、子03公開・退役/trace/451が未完。今回kernel部分だけでACCEPTEDにしない。439は残構造branchの調査で除外/人工到達の許可ではない。BUG1159修正d93d4faae、当資格再試験完了、Production全正式品質は未完。
