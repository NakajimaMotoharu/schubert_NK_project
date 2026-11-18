# JaCoCo二進session時刻符号境界の単体仕様

NK-OPS-001、`jacoco_readonly_exec_subset.decode`、WBS-P018-08.03/2、BUG-3322／YKT-2694、SS354・451。元工具の12ベクトルを保持。固定header・session名・class recordは手作成し、時刻8 bytesはPython標準 `struct.pack('>qq', ...)` で符号付き二整数として記録する。期待値はJaCoCo SessionInfoのJava signed longと非負・順序の契約から固定する。

| Test ID | 入力の開始、終了 | 期待 |
|---|---|---|
| TOOL-COVERAGE-EXEC001 | 0、0 | 同じ二時刻を受理 |
| TOOL-COVERAGE-EXEC002 | Long.MAX、Long.MAX | 同じ二時刻を受理 |
| TOOL-COVERAGE-EXEC003 | 0、Long.MAX | 同じ二時刻を受理 |
| TOOL-COVERAGE-EXEC004 | -1、0 | 拒否 |
| TOOL-COVERAGE-EXEC005 | 0、-1 | 拒否 |
| TOOL-COVERAGE-EXEC006 | Long.MIN、Long.MIN | 拒否 |
| TOOL-COVERAGE-EXEC007 | -1、-1 | 拒否 |
| TOOL-COVERAGE-EXEC008 | Long.MAX、Long.MIN | 拒否 |

元12と新8ベクトルを9件のunittestで確認する。独立境界、順序、符号、無効レコードの既定項目を含む。実native、実行中session、製品coverage、並行・再送は純decoderの対象外。元と修正後のコマンド、入力hash、終了を対の結果へ保存する。
