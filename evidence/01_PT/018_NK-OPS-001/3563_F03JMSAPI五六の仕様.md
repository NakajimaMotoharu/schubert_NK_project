# F03 JMS delivery/log47とAPI borrowed/owned9の文脈照合

Program NK-OPS-001、対象はinput/041の56 raw ordinal/class/method/行。現Main28af・PG19740/19742/19744、元1491観測を保持する。旧PG16350/16356のwhole-source SHA・全PMD属性・manualPurpose・manifest直接宣言hashを照合し、現在SS321/324のowned close/fatal/rollback規約とSS312業務transactionを独立に読む。旧成功PTを移すものではない。

送信側primary Error保持とdispatcher別close Error優先は異なる。捕捉はcleanup/未確認rollback/固定失敗の境界であり、実provider停止・DB commit・graph有限帰還・wire消去の実測を意味しない。API借用transactionに新commit/close権限を付与しない。正常/異常/null/同一Throwable/通知失敗/再送/並行はdynamic必要後条件として残す。

操作: PYTHONPATH=tools/quality python3 -B evidence/01_PT/018_NK-OPS-001/input/023_owned_f03_source_context_metadata.py run（続いてpost） evidence/01_PT/018_NK-OPS-001/input/041_f03_jms_api_purpose_decisions.json。Python read/hashのみ、Product/Test/JDBC/JMS/Root/VM実行なし。独立postは全1491 ID/ordinal、unique1439、duplicate52、前982+新56+残453、current source/SS hashと保留範囲を再構成する。line/method/class/branch coverage未測定、PT PASSへ算入せず、F03/451/新leaf受入は0。
