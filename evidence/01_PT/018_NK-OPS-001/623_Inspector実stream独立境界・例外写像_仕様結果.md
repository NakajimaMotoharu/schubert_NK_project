# PG1007～1021 Inspector実stream独立境界・例外写像

Program P004-04 / NativeReader.executeStreaming、queryFailure。RD OPS009/UI251/SS341§7.4・SSC125/451/PG-D411。全体正式はPT-WEB-20260925-24/1964PT/53scopeのまま、当局所成功を全工程完了へ加算しない。

| Test ID | 独立入力・期待値 | 観測結果 |
|---|---|---|
| PT-DEP-1007001 | start一回が公開canary IOException、固定COMMAND_FAILURE/cause・suppressedなし | PASS |
| PT-DEP-1007002 | 実`/usr/bin/printf %s ABCD`/ABCDE、limit4、手書きASCII65,66,67,68／5byte拒否、各三stream実close1回、child終了0 | PASS |
| PT-DEP-1015001 | 実child＋低位readがIOException/IllegalStateException/NPE/AssertionError、既知固定診断／未知同一object、三stream close各1、child終了0 | PASS |

全34PT/4suite/F0/E0/S0/flaky・rerunなし/SpotBugs0、43.507051s、Java25.0.4/Maven3.9.12/Linux host。command `python3 -B tools/quality/vm/050_s1/pg1020_stream_selected_v9.py`、branchdev-foundation/source d4faf8e7eadd2d22563e15380ff80f43883cd6a8、終了0。実Maven CLI/XML hash/source/start/endは私有run.safe.json、公開数値はqualified.safe.json参照（raw/credential/session/cookieなし）。line129/129、method20/20、class1/1、branch24/24、instruction586/586、除外0。局所XMLは新timestampと一意test名、三追加test存在、static0を独立collector1021で検査。batch JAR568class entry中NativeReader1のみ変更、567entryは926同byte。JaCoCo解析対象343classとJARentry568を区別する。

期待値はProduction methodから生成せず、literal入力、固定domain理由、object identity、独立close計数、実OS終了codeに基づく。正常/限界/超過/I/O/未知/null故障/並行virtual drainを含む。deadline・再送・ownerは既四suiteの独立観点を併走し、実VM同owner/native経路は未受入として別管理。

## 失敗保持・原因別是正

- BUG1006/YKT775：selectedv1～4は依存root plugin/0件filterで対象PT未実行。全体PG1011へ是正したが新TDD oracleF1でactual1。合格加算0。
- BUG1007/YKT776：stdout close後IOException必須という新期待値はEOF契約と矛盾。三streamの実close計数＋実delegateへ是正し、PG1014は33PT0。PG1015読取faultは上位readNBytesをoverrideして低位委譲を捕捉せずTDD F1、PG1016は低位readへ訂正し34PT0。ただし当旧mainのline212は128/129、未達を保存し100認定0。
- PG-D411/BUG1008/YKT777：既知例外値をdomain型へ限定、未知は元helperで同一throw。PG1019は34PT0だがstatic2/actual1、PG1020は34PT/static0/四counter100。static抑制追加・範囲拡大0、外部仕様/SS期待値変更0。

## 保全・再現・hash

Work root `/home/mini/codex/project1/work/pgpt-runs/PG379/`。PG1011失敗の全XML/execは1012へ不変更保存、旧全体成功・旧失敗slot再利用0。

| 証跡 | SHA256 |
|---|---|
| pg1012-stream-failed-preservation-v1/manifest.safe.json | d90aea90f71ff25fa6e6751027d76c724b4ebd0918594987c1d8a0e29c5eda54 |
| pg1013-qualified-dependency-cache-v1/manifest.safe.json | be11e10554ee109ad344a30b15d060db2e95818e2be9ede535fd52718781074e |
| pg1020-stream-selected-v9/qualified.safe.json | 238e467689b8f846de843384feef1da63821789e11464e7acb61ba5be4d3a5a5 |
| pg1020-stream-selected-v9/batch/jacoco.xml | ad49e4a823d0321d25202b787a1598ce08f2faea0fec7cba86e6667734bf54c8 |
| pg1020-stream-selected-v9/batch/spotbugsXml.xml | 2e7c30a9709b8f1b50c28acb9826f5bec45e83605f2297891bc7cd0bdf5b4506 |

Cacheは合格済926のprotocol174/storage72/bootstrap102全byteを取込み、既cache全fileのprivate preimage/hash保持（PG1013）。新全体回帰・新署名/native/formalは未完、旧40ef native10を新classへ流用しない。次1018 fresh全六→1022 source/XML/session/static/全1632entry資格。各run新only、再発行しない。
