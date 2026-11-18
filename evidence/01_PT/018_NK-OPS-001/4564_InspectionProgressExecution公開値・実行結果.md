# InspectionProgress／InspectionExecutionの実行結果

PG38364/66/68、Unit ebe82da11af710f830a8cdd7129c7a0cddd04d3a、Core 47aeed19a157661363ffab5c4b5054f6b20230a1。Test ID PT-OPS-INS-VALUE-005～009は初回全5成功、失敗・エラー・skip・未実行0。静的指摘0、独立XML／物理4CRCに一致。JDK25／Linuxでの実行手順とUTCは各manifest。

対象3物理型の生実数は32行／23メソッド／3クラス／29分岐／262命令が到達。分岐1・命令6が未到達。既定レポートからは隠れるjavac生成defaultが原因であり、BUG-3223へ起票した。依存InspectionRunの実測と旧結果を合算しない。実DB、全Inspector、実native、正式WBSは未受入。

証跡 evidence/01_PT/018_NK-OPS-001/evidence/PG38368-p00404-inspection-execution-progress-independent-v1/manifest.json SHA256 8a72b022aa6cd8541fcfab28a35cbd931ef3ca2bdfb83764f8f079109429eadc。
