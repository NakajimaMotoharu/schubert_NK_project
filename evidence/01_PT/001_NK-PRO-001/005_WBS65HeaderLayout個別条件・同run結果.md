# WBS65 Header・Layout・Fieldの現在host個別条件

対象source `2a5cdab45c6ef5e32994264cf1e93f5d70216040`、Production Main `7aed8eace7c844c2f79f2e39db766faf914890d5`、run `PG26240-PROTOCOL-NAMED59-FLAG6`。全124通常PTの同source結果を再実行せず参照し、PG26250と独立PG26254で個別条件を照合した。正式1964PT/53scope、歴史的17受入は更新しない。

| Scope | Source/物理 | line | method | class | branch | 個別条件 |
|---|---:|---:|---:|---:|---:|---:|
| P00101 header | 6/6 | 137/137 | 30/30 | 5/5 | 88/88 | host3/3 |
| P00102 layout | 20/29 | 564/564 | 84/84 | 22/22 | 170/170 | host3/3 |
| P00201 field | 43/43 | 457/457 | 121/121 | 39/39 | 188/188 | host3/3 |

UI233正本64行と独立TSV、UI234～236の389物理項目が一致。WLGEVT01のLog type/Action説明二差は短縮表現であり、QA054の閉じたREQUEST/HTTP_REQUEST_COMPLETED-or-省略、ACTION/MENU_VIEWEDの組合せを独立literal byteと13通常caseで確認。fixture/production/oracleは変更しない。

MSG001の実JMS、MSG009の全管理文書・設定LF、actual backend/native/CHRとglobal451は当pure componentの範囲外で後続ownerへ保持する。Shared PayloadSemanticValidatorは同run参照であり所有・費用を移さない。既定filter214を全名/理由で記録しruntime未測定へ換算しない。自然branch0はN/A、各sourceでbranch正数と偽らない。

BUG2647/YKT2327は工具の列数誤りを修正前登録し、物理五列差/未記録説明差/証拠不足の三反例を拒否。元exit1証拠PG26252を保全し、製品試験の失敗には数えない。

実commandは `python3 -B evidence/01_PT/018_NK-OPS-001/input/1168_header_layout_field_current_criteria.py` →終了0、`1169_header_field_independent_post.py` →終了0。OS/JDKと元124のcommand/真正終端/静的解析は同run親manifestを参照。追補はmetadata処理のみでJVM/VM/DB/鍵/held class IOなし。

証跡: `../018_NK-OPS-001/evidence/PG26254-header-field-independent-v1/manifest.json` SHA256 `6c1c4cab4b794126af401de1b3e708141adc6acbc2b6d7e48a4f3abe0b0d907e`。親PG26250 SHA256 `74f615ceb33c98fcea90f20ff0fd72c929c7afac61d648f47bb034aaf0686bc7`。要求/TestID/期待値の全対応は親のrequirement-oracle-matrix.json。
