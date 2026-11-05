# F03 Thread残83の個別文脈照合

NK-OPS-001 / input044は原DoNotUseThreads残83を全ordinal・class/method/variable/行で固定。Main28af/normal19740/SB19742/raw19744を不変とし、管理pool1/queue32、明示owned worker/hook/reader、owner-thread identity、固定診断signature、interrupt/有限pauseとUNKNOWN tickを個別に読む。規則の一括無効化ではなく現在設計のstandalone所有境界への適用判定。

API/Web entry IRQ表、実joinとstop要求、owner/self-join、TERM-before-reader join/wipe、LIFO trace scope、UNKNOWN interval帰還とowning frame保持の差を維持。未計測のrace/実資源解放/deadline・native・coverageを認定しない。Thread/Executor/handler/hook/Root/DB/VM/fixtureを起動しない。

PYTHONPATH=tools/quality python3 -B evidence/01_PT/018_NK-OPS-001/input/023_owned_f03_source_context_metadata.py run（続いてpost） evidence/01_PT/018_NK-OPS-001/input/044_f03_thread_remaining_decisions.json。独立post: 1491=前1126+新83+残282、原ID/ordinal/unique1439/duplicate52・current whole source/SS/POM/JAR、保留partitionを再構成。PT合格/四coverage/globalF03/451/新leaf受入へ加点しない。
