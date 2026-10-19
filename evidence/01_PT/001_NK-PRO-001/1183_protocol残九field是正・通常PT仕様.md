# protocol残九field是正・通常PT仕様

2026-10-20、Program NK-PRO-001、WBS-F03主担当/P001-01参照追加費0、BUG1476/YKT1237。SS321/322/323/333/354、411/451、462/PTPRE001～003。承認済み外部仕様は変更しない。

対象：ContentDisposition、InteractionKind、MessageKind、ResultCodeのprivate wireValue→encodedValue、およびBrokerTopologyのprivate address/queue/fullyQualifiedQueue/maximumBodyLength/timeToLiveMillis→encodedAddress/queueName/qualifiedQueueName/bodyLengthLimit/ttlMillis。public method、constructor引数、constant名/順序、全wire/address/queue/TTL/body-length literalは不変。先行semantic十八と合計23型/27fieldを静的照合する。

独立期待値：HeaderModelTestの固定header、BrokerTopologyTestのSS321手書きliteral表と未知/null、ProtocolSemanticTypeTestの承認済み表、既golden vectorのoffset/length/padding/NFC/負入力を保持する。PT-PRO-F03-ENUM001は1181の固定Java enum stream全byte/読戻し/EOFを不変更。ENUM002は明示型を18→23へ拡張し、全型のserialized field0/UID0を確認する（method名は既TestIDの安定性のため保持）。既成功からexpectedを生成しない。

実行前判定はPT_DEFAULT。有限合成byte/メモリstreamと自己所有snapshot/target/Maven/JVMのみ、offline、通信/DB/JMS/サービス/VM/実credential/配備/失敗cohort回収0。BrokerTopologyはbrokerを起動しない値catalog。immutable final fieldのみのrenameで新しい並行/再送状態を追加しない。null/未知/空/境界/例外は既codecとcatalog試験を含むprotocol全88件/18suiteで確認する。

新clean commitをsource固定後 `python3 -B tools/quality/pg5728_protocol27.py` を一度実行する。JDK25.0.4/Maven3.9.12/JaCoCo0.8.15/SpotBugs4.10.4.0、format→compile/型null→全protocol PT/package/coverage/SpotBugs。FES/flaky/rerun/not-run0、XML全88一意一致、source固定、line/method/class/branch全miss0を要求する。旧6b6の88結果を新sourceへ転用しない。

別点検 `pg5729_protocol27_static.py` はPTを発行しない。元6dbとの全23file/27fieldの厳密private-onlyモデル一致、実javap全公開ABI/opcodeのprivate名/CP番号だけ正規化比較、当source全849Main/実aux1664をPMD/Checkstyleで分析する。他5moduleはsource不変かつ旧物理class hash一致を確認した入力のみ、fresh全体compileや旧PT成功の合算を主張しない。PMD警告exit4は維持、当27警告消失と全体F03受入を分離する。

元source/archive/command/実開始終了/exit/XML/hash/coverage/型null/staticは各new-only safe manifest、公開許可列はPG5730に保存予定。新全体/native/CHR/451正式・WBS leaf終了依存は別途未受入。拒否PT代替件数0、PTALT001/002未特定部分は保留し、通常独立PG/PTは477の現行自走条件で継続する。
