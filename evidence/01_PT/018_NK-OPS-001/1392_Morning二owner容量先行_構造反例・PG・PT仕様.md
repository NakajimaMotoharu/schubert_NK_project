# Morning二owner容量先行：構造反例・PG・PT仕様

Program NK-OPS-001/MorningStartupLaunchOwner.sequence、OPS009/UI251/SS333343/BUG1582/YKT1335/PG-D481。SSの取得前準備・逆順owner停止の既契約に対する内部実装是正であり、業務/RD/UI/SS/期限/権限/固定外部結果を変更しない。実装前に915/916へ起票済み、QA/SSC追加は不要。

原source5aa08a26e/6440・6442q0a1a830eを保全し、[6446旧構造証拠](evidence/provisional/PG6446-sequence-capacity-old-gap-v1/manifest.json) SHA `a7342dfe9af341f056cced3977095451f7303706c8fb4d71c6c09f1e14cf7b53`を取得。原Batch全class/sourcehashとJDK25.0.4の実JVMを照合し、noarg ctorのbacking array長0、API返却後の初回add→grow、catch listには未登録を確認。これは静的な取り落とし窓の証拠で、実OOM発生やPT失敗と偽らない。JDKコード全文や実秘密dataを公開しない。

PGは`new ArrayList<T>()`→`new ArrayList<T>(2)`一行だけ。最初のlaunch前に固定最大二slotを確保し、正常API→Web、immutable earlier/completion snapshot、null/例外identity、既逆順stopを維持。既Test byteは全固定、赤/診断Test SHA7529b477も不変更。formatter74915終了0・構造解析の旧正/不正容量/追加add/外部alias拒否を含む二工具0、三工具pyflakes0。新実PTはまだ未実行。

## 通常PTと静的証拠の分離

PT_DEFAULT：自己所有のJava callback/文字列/リストだけで、既sequence428007～009（API→Web/immutable list、launch各stage IO/Runtime/Error・逆順stop、null）と当診断6件＋baseline12＝関連23件/10suiteを実行する。同fixtureの内部matrixを件数へ水増ししない。原成功23の再確認目的ではなく、一行PG後の同独立oracle再試験である。実Root/DB/Unit/VM/native/intent/permit/cohort操作0、実heap枯渇を誘発しない。

`PYTHONPATH=tools/quality:tools/quality/vm/050_s1:/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime python3 -B tools/quality/pg6448_morning_sequence_green.py`

source=当PG保存commit。6448は旧5aa→当sourceの差を一Main・正確な一行置換だけに限定し、全Test/gates/Current不変を確認して新only slotへ一回起動する。終了0後だけ6450が原XML/六Jar/全8511667/実counter/PMD・Checkstyleを照合し、6446 currentがcapacity2 ctorの先行・正確二launch/add・外部mutable alias無しを原JVM/JDKで確認する。current資格SHAは未取得なので現時点Noneで先走り拒否。静的なallocation順序を実測PT PASS/coverage/nativeへ加点0。

既ApiMessagingRuntimeは三group容量先行、SyncRequestConsumersは四context容量先行の同原因是正例としてsource/JVMと当physical一致を横展開で個別再照合する。既成功PTを新Morningへ移植せず、他収集候補/保留Root scopeが未確認ならYKT1335はOPEN。関連commit/再試験/coverage/hashは後続結果へ記録する。

本群.25/.75/2ppは追加発見として固定し、診断326群/未完通常50群/原-v4と混同しない。正式1964/53/17-190/工数null/QA051final/BUG1581・1582/全YKT未完/PTALT不明代替0/実環境HOLD・全保全維持。通常小群で停止せず、同経路の変更群をまとめて必要全体へ進める。
