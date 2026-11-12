# P01501 QA049 完了metadata原12件通常PT

NK-WEB-001/SS314QA049/PG-D356/TOKV201..205、WEB009..015。PG27402で確認したSessionAttributeCodecのencode completedAt lambda（line78）、legacyv1でcompletionを拒否するbranch（line130）の不足7I/1M/1Bを、whole既存JSON7＋V2五の全12件で補完する。既合格Payload9/Id4/fatal5/helper4の確認再演とexec合算を行わない。

独立期待値: TOKV201 issuedAt一致/+1ns/+1s completion許容、-1ns/null拒否。TOKV202 v2固定JSONbyte/完了時刻固定UTC（0・micro・翌日）。TOKV203 legacyv1未完了だけ/v2再encode、rootのformatVersionが後でもv1completedAt拒否。TOKV204 null/型/未知/重複/時刻正規形/完了前/版整数以外拒否。TOKV205 pending＋consumed混在10個の固定JSON・11拒否・100並行で同じ独立literal。元JSON7は4115・001の全期待値を保持、expectedをproductionで作らない。

BUG2706はV2fixtureの唯一pool TWR.close無期限をfinallyshutdownNow/await10へ修正しFuture20と元全assertion逆変換一致。原fullfixtureを抽出せず、public value/JSONだけ、API応答の真正性・complete業務許可や権限を偽造しない。型へcompletionを渡すのは承認済み閉schemaの通常負例/正常値試験であり、privateSnapshot/HMAC/authの代替としない。公開UUID/時刻だけ、配備key/session/VM/DB/network製品IO0。

着手追加費.075/.225/.45pp cap1（finitefix.025/.075/.15、必要12資格.05/.15/.3）。Mainfa9b9fa8/全15source16class+Proto176はPG27390の完全同byteを使用、再buildなし。JSON7Test classも同byte再利用、V2Testだけ新javac/PMD/CS/GJF。PG27418でrootNullAway/SpotBugs/既JSON静的同source再利用・V2 raw6個別非該当/抑制0を確認。JDK25.0.4/JUnit1.13.4/JaCoCo0.8.15/Gson2.14/annotation2.48/JSpecify1.0.1、全CP/hashをmanifestへ結合。

実行 `PYTHONPATH=tools/quality python3 -B evidence/01_PT/018_NK-OPS-001/input/1623_session_v2_12_profile.py run <固定Test source>`、PG27420一回全12、PG27422で元OS終了/XML/TestID/CRC/全192/init/四counterを独立照合。自然0branchはN/A、依存未実行を除外せず全192partialを保持、target schema/token四100は実測成立時だけ記録する。BUG2706/YKT2374限定六owner・原190新0/正式1964-53・工数null、実DB/actual4/業務tokenlifecycle/全451終了は別未受入。
