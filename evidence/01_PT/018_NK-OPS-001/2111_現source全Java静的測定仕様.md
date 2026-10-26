# 2111 現source全Java静的測定仕様

event2457/WBS-F03、着手前2/4/8pp cap10、source370fd74f6/Main21d7c304、PG10632正常compile inputを固定する。直近は四Test等の限定静的測定しかなく、元global source5224/PMD2217の成功・適用性・件数を現sourceへ流用できない。全体scopeの現source指摘と次の具体的是正対象を得るため、一度だけPMD/Checkstyleを再測定する。確認だけの全PT回帰は行わない。

対象は正常10632 input inventoryにある六moduleのsrc/main/java965とsrc/test/java845、計1810。原inputと現worktree/source snapshotの全対象SHAを確認し、既存PMD7.28＋record1298修正jar、Checkstyle14.3、固定rule二ファイルを使用する。ルール/優先度/除外/抑制を変更しない。tools、保留二file、私有raw、DB/Backup/鍵実体は対象外であり、その内容を読む操作はしない。

PG10688は新規専用SLOTにsource-list、各command/時刻/own PID・親PID・exit/stdout/stderr hashを保存し、元正常snapshotのMain jar/公開依存jarをtype解析に使う。annotation processor/製品main/Test/VM/サービス/ネットワークjobを起動しない。解析のJVMと通常ツールファイル読取・新証跡writeだけ。sourceを解析中に変更しない。input/依存/tool/ruleは終了後も再照合、実exit/processing error/rawfindingを保持する。長時間なら同じown sessionへ再付着し二重発行しない。

PG10690は両XMLの別集計、source/list/snapshot/dependency/tool hash、全findingの原属性/行とmodule/Main-Test区別を独立点検しindexを保存する。syntax指摘を自動で欠陥・非該当と認定せず、適用性はsource文脈と後続成果を突合してから判断する。予期せぬtool障害は915/916先行起票、raw非0を合格へ正常化しない。静的測定の実行完了と全F03/451受入は別。

TestIDはF03-CURRENT-SOURCE-001(input)、002(PMD)、003(Checkstyle)、004(独立post)。正常は完全scopeと原hash一致、境界/異常はxml/schema/欠落source/違うhashの拒否、null/並行/再送等の製品観点は当静的工具へ非該当であり元PTを免除しない。新PT/PASS/coverage/正式認定/工数率への換算0、動的HOLD・QA051final不変更。
