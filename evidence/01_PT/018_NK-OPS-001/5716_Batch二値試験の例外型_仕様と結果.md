# Batch値試験の例外型

NK-BAT-001、WBS-F03/2-2-b、P017-02.01／P017-07.02、RD OPS009/DAT009、UI251、SS331/332/341。2799の `PT-BAT-130～137`、2747の `PT-BAT-154～161` の固定値、順序、所有を用いる。対象三宣言はPT-BAT-135、137、161。[BatchStep仕様2799](2799_BatchStepValues原八件_単体テスト仕様.md) [Cleanup値仕様2747](2747_BatchCleanupStep原whole10_単体テスト仕様.md)

BUG-3614。正規Batchの許可済み14物理だけで、合成recordの反射と有限並行を厳格Javaコンパイルした。反射を `ReflectiveOperationException`、Futureを `InterruptedException`、`ExecutionException`、`TimeoutException` に具体化。三宣言・四import以外は元のbodyとbyte一致。

実行PG42780、対象 `50328c4d59292842c38c61e76721ddd426635a18`、dev-foundation。通常16成功／2 suite、失敗・skip0、SpotBugs3→0、Checkstyle0、PMD生13は固定のworker／終了条件・合成recordの診断の報告を保持。静的抑制・除外0。実DB、FFM、削除や所有権変更は実行していない。製品変更・新定義・正式受入0。[PG42780](evidence/PG42780-f03-batch-value-fixtures-checked-types-v1/manifest.json)
