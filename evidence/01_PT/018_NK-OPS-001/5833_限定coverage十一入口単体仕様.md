# 5833 限定coverage十一入口の矛盾拒否

WBS-F03/2-2-b、451 §5、BUG-3799、YKT-2961。テスト対象は Python 3 の各coverage validator。製品・実行プロセスに接続せず固定XMLだけを各入口に渡す。1 method／8命令／3行／1class、分岐の条件は各入口の既存値。

| 入口 | methodのみmiss=1 | method欠落 |
| --- | --- | --- |
| 027 Question Receipt | 001 | 002 |
| 028 Stub | 003 | 004 |
| 030 API Sync | 005 | 006 |
| 031 Web Reply | 007 | 008 |
| 032 Web Log Worker | 009 | 010 |
| 033 API Web Log | 011 | 012 |
| 034 API Messaging | 013 | 014 |
| 035 Log Router | 015 | 016 |
| 036 API Log | 017 | 018 |
| 036 API Ready | 019 | 020 |
| 038 Web Request | 021 | 022 |

すべてPT-OPS-F03-EXT-COVの末尾番号。独立期待は元XMLを受理し、他の同じ数値を保った上で二不正を拒否すること。028と036 API Logの実分岐なしを許す既条件を維持。027は既集計BRANCHの存在条件を維持。029・021・022は個別確認を残す。対象source・終了・証跡hashはPG44566へ記録する。製品PT又はcoverageの増分は0。
