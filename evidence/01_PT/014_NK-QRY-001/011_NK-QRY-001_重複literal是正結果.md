# 質問照会Testの19重複literal是正

2026-10-26 14:23 JST、BUG1812/YKT1563、群2349→2350/F03（原P01401/P01403関連0）、開始1/3/6 cap10。対象はQuestionQueryApplicationServiceTest12定数とQuestionQueryReplayServiceTest7定数。所定PMDの既19duplicate指摘を、同じString literalのcompile-time定数化だけで是正した。元108assertion/全@Test/業務fixture/SQL/期待電文を変更しない。

source4c975c3eb1d8d5540805fae642b80d0d5e781c12、Production Main21d7c304不変。Java25/Maven3.9.12/PMD7.28.0/Checkstyle14.3.0/GJF1.36.1は010同環境。実command=tools/qualityの下表pg10298/10300/10302/10304各Python工具、PYTHONPATHと全stage command/tool/source/version/hashはmanifestに保存。

公開pathは `evidence/01_PT/018_NK-OPS-001/evidence/provisional/` 下。

|path|真正結果|SHA-256|
|---|---|---|
|PG10298-query-test-literal-plan-v1/manifest.json|PMDの実token位置から19literal/全参照を列挙、逆展開で元全token一致|17887da431084a7c24ed4299f83ebe0d948f0d8268d0e44cc62e07b2e6988aa6|
|PG10300-query-test-literal-static-v1/manifest.json|raw9/CS0/processing0/exit1、duplicate19解消|c82dc0dfd69a1abfe9fafa4d89d05d58c9c2caea7c57ac6c6cc16f909913272f|
|PG10302-query-test-literal-six-compile-v1/manifest.json|当source六jar正常compile/NullAway exit0、PT0|f71fc6274ba7f881e0a11d84190edce8bf71e14cbd0936a4d92a471acdd86eaf|
|PG10304-query-test-literal-post-v1/manifest.json|元全token/assertion108保持・四metadata反例拒否/全Main1843・他Test1940同byte/当二outerだけ変更|f468fca21fd5601f4a620cca5564ed022878a0831a09499f559bf172006e1904|

19定数の別値化・assertEqualsの非同値化を二source各二変異で検査し拒否。元expected helperとnormal classは212 sourceと同byte/同source SHAを確認し、独立24vectorを確認目的で再演せず歴史メタ資格として参照する。これは旧製品実PTを当sourceの実行へ転用するものではない。

raw9は010の文脈九と同一。10304のpmd-applicability.jsonは当source hash/実line/textへ結合し、六Standalone Test JDBC interface loader/明示constructor null負例/checked ExceptionをAssertionErrorへ変換するcallback/二回目openのfixture ordinalを個別記録した。contextual applicable0、抑制0/rules変更0。raw1を0へ書き換えず、全F03・他source静的合格とはしない。

元業務PT NOT_EXECUTED_HOLD/coverage未測定、新製品TestID/PASS/個別受入0、全G03/451/CHR/native/正式1964-53/17-190/工数null/QA051final・全安全HOLD不変。当二Test SHAは次batch traceまでpending、旧runtime/費用を保持する。
