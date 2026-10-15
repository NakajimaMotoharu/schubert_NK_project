# Media全scope・横断要求個別照合（品質接続待ち）

2026-10-15、WBS-P003-02、Production a9/PG2802。正本origin/main756a891d9のRD131 MQ019/020・RD132§5 MSG-F01/F02、UI235 MEDIA1024・237§8、SS333§8～10。専有四pathはfile/ContentDisposition、MediaDescriptor、MediaDescriptorValidator、MediaTypeで485と一致。終了依存P002-02は同a9受入済み。現在の個別判定はNOT_ACCEPTED、全3704/別独立/nativeと原XML witnessの接続まで先取りしない。

## 全型・method・独立期待値

MediaDescriptorのconstructor・全八accessor・redacted toString、Validatorのvalidate/validateStoragePath/validateFileName/validateMime/extension/hasDotSegment/validateCanonicalText、両enumの全定数とContentDisposition.fromWire/wireValueを対象とする。専有外semantic.ContentDispositionとの混同、Browserへのstorage path公開をしない。

MediaDescriptorValidatorTest七methodを001のM01～M03および011のM04へ対応付ける。七MIME/拡張子・種別/root prefix/I-AはSS333の手書き七行がoracle。cross product、storage/表示拡張子不一致、Video attachment、未知/大小文字/MIME別名、非NFC/空/末尾space/制御文字/絶対path/空segment/dot/backslash/quote、SHA64小文字hex、N12の0/1/上限/超過を検査。constructorの参照七引数nullおよびvalidator/fromWire nullは内部非null事前条件違反として拒否し、catchして成功へ変換しない。

M04は独立UTF8 3n+rでlogical64/path512/name256byteの正上限と一byte超過を構成し、全七形式のdescriptor八値・N12=999999999999をliteral比較する。pathは各OS segmentが255byte以下、256byte表示名を実storage名と混同しない。enum values/name/valueOfとI/A/未知wireも独立literalで検査する。全入力は公開fixtureで、実素材/masterを使用しない。

## RDとconsumerの責務境界

| RD | 独立照合・consumer Test ID | このleafで認定しないもの |
|---|---|---|
| MQ019/020 | MED055～061は実PostgreSQL metadata/認証→file inspector→Inbox commit→固定descriptor応答、MED060は実Artemisでcommit後reply・再配送・同ID再送のDB一行/固定応答。MED037～040はUI232/235 byte offset手組で3要求・七形式・成功/error・correlation/contextとdescriptor全値を照合。MED027～032は独立patternのHTTP Range/HEAD/attachment/20枠/100並行/故障時資源解放 | この四型だけで現在VMの認証/Root/HTTP ready、API/MQ全体、IT/ST合格を発行しない |
| MSG-F01 | MediaのMQ dataはMEDIA1024（Video付随metadata込み1808）だけで素材本体なし。上記原wire手組とactual reply exact比較を根拠にする | mediaそのもののbyteをMQへ追加しない |
| MSG-F02 | RD132§5は大容量結果file受渡し。record長/件数はSCNRSP01のfile descriptorに属し、014/P003-01のD01/D02・R02・writer/readerを参照する。媒体descriptorにはUI235/SS333承認済みのID/path/size/hash/type/MIME/modeを検証する | binary mediaへ未定義record長/件数や応答MAC fieldを追加しない。全要求の工程終了は関連ownerの閉鎖も必要 |

004/005等の保持directory能力は別主担当の受入を参照し、共通製造費を再計上しない。media二型が渡す相対pathは能力ではなく、consumerのNOFOLLOW保持inode/size/hash/現認証が別途必須。DB/JMS transaction・再送・HTTP・実file後条件の上記既存試験を原全体XMLへ接続する工具3356はROのみで新PT加点0。新M04は関連3348の14 Protocol試験内で成功済みだが、個別qualityは3350/3352/3354の同source・全四counter・静的・独立oracle・全scopeまで待つ。

実環境/command/source/終了code/coverage/hashは012と今後の同群全体結果に分離保存する。現在Main/設定/外部仕様不変更、RDF/UIC/SSC追加なし。正式1964PT/53scope・工数null・QA051final保留・全PGPT/ITST未完を維持する。
