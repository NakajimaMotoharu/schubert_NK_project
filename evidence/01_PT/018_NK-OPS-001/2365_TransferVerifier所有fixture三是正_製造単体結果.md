# Transfer verifier 所有fixture三是正：限定PG/PT結果

2026-10-28 / 2364 / PG-D752 / BUG1991-YKT1739 / source8ccadeed207cf1f38264c35199bd4def12aae6c3。Test一だけ変更、Main/設定/POM/他Test不変更。TestInput→ChunkedInput八identifier/ifのZERO_PROGRESS_MODE一と、closed疑似channelの元三assertを囲うfinally同一object回収だけ。元全tokenへ明示回収域を逆変換し八非同値負例で保持、新TestID0。

| 証拠 | SHA-256 / 実結果 |
|---|---|
| 12664 plan | ea86a69bf4b7ca5d5aa70d7d1f825b6f80b1ee543eaeaca122dbb113c90bb155 / actual0・逆/八負例 |
| 12666 normal | 138b454a9eb9d3d00f6ac2579d6f76b36afbc340b745375d53dfa8383bf59e10 / session27245真正0・六module/PT0 |
| 12668 original host | 1a49b9f669459d939feac578475608fe79836336328fe471fa8c2272bf383a4b / session75811真正0・原3/一suite/FES-aborted0 |
| 12670 static | 9aadfc3732078e310172ff095fd03290e3544530e662db99ef341fbd98dddbe8 / session59261真正0・原三→PMD/CS/processing0・抑制無し |
| 12672 independent post | 5606c98f263fd7d0aeb157199382fad6b8513c51955c383f5bd7f20511483ad7 / session59896真正0・実XML/一execCRC/全source・全Testとinner一対一/全三artifact |
| 12674 trace / 12675 post | ec60fdb82dc9c3ab811832d6b0e99342a88cdf39cec0a437c7c465ae55a24af6 / 0925d73a86fa6fca5d33f08011989bcb89f18cf397244fdd689378d8d2a7a912 / actual0・983一SHAだけ他982不変/元owner-costP00803/全WBS同HOLD1 |
| 12676 delta / 12678 post | d09c1ac0fe1e7d5b110376bf49a2d9ebe3086d757bf86822b3202798628f3d0e / 266322bbe3f49af73a8d95713a0db0dd06c78661a4b1bfe5519125eefdc44795 / actual0・原三IDだけ是正/九反例 |

各entryはchecked一file入口（実argv/tool hash/OS/JDK/開始終了はmanifest）。TC421既定Java25.0.4/Maven3.9.12/JUnit5.13.4-platform1.13.4/JaCoCo0.8.15/PMD7.28-record1298/Checkstyle14.3。原W06の全3methodをexactcatalog・ja-JP/JST・独立一execPG12668-TRANSFERVERIFIER-JPで一回だけ実行。元仕様の独立4800byteと自前hash/1-201-10000件/32位置改変/部分read/maxbuffer/全正常・異常・null・caller非closeを維持し、Mainのverifyをexpected生成へ使わない。

## 自己所有のfile後条件と物理差分

Pythonが新SLOT配下へ0700 own-java-tmpを作り、その絶対pathを-Djava.io.tmpdirへ固定。Jupiter組込み@TempDirをALWAYS cleanupで使用、外部extension自動発見false。原合成file最大合計48,969,600byte、CREATE_NEW→自分が生成したfileだけread/TWR。元の保持root・unknownfile・原本/DB/鍵/Backup/VM/Root/FFM/権限/permit/intent操作0。試験後は専用temp root/CWD双方空・root inode/device/mode同一をhostと独立postで確認。未知の残骸を削除して成功へ読み替えず、今回は残骸0。

全Main1843byte不変、Test全1962はold inner TestInput一をnew ChunkedInput一へ厳密一対一対応（元SourceFile一致）し、親Testとinnerの二physical差/他1960同byte。Inner rawCode表現同/debug差、親はfinally追加によりrawCode/debug差、名前変更によるCP/self type差と意味保存を全token逆/実3で別確認。独立metadata reader三正常四異常、未許可Product probe0、JDBC/Artemis load0、全source/dependency/helper前後同byte。class名差を欠落Testや追加業務classと混同しない。

## 実測counterと未証明事項

TransferContentVerifierは20L/1M/1C/10B全miss0、空private utility ctorはJaCoCo既定filterで非計上（sourceは全byte検査）、人工呼出し/reflect/除外追加0。StorageIoException4L/2M/1CとReason4L/1M/1Cはmiss0・branchは元分母0=N/A。LargeResultContentはcovered6L/2M/1C/4B・missed1L/0M/0C/4B。Record/enum等の既定filterは不変更で、source上全宣言の受入免除に拡大しない。

完全API467physicalはcovered20L/1M/1C/10B・missed12719L/1841M/364C/4812B、Protocol176はcovered6L/2M/1C/4B・missed3474L/741M/158C/1010B、Storage80はcovered8L/3M/2C/0B・missed1231L/291M/37C/533B。全artifact未達/既定package metadataは保持、旧exec合算/手動除外0。

Mainが宣言するNoSuchAlgorithmExceptionのprovider故障は今回注入・動的確認していない。JaCoCo四counter100%は暗黙の全例外経路/全JDK provider/全SS契約の証明ではなく、この未証明を全451完了へ読み替えない。保持inode属性/認可・directory capability・writer公開/再生成・実環境/CHRも本hash部品の代用範囲外。

原三ID02669/02670/02671だけ是正、raw8498/累計919/Main1506-Test6992/追加8保持/refs3175-pending784-未参照5323、全解析再発行0/actualViolationCountnull・新分類0。BUG1991はVerifier対象限定再試験済みだが、YKT1739には別ScenarioRecordStreamTestのclosed FileChannel共通候補が残る。該当Test全文は確認済み、writer/codec closure未資格で今回実行/修正していない。横展開全体をcloseせず後続へ渡す。

実装済み工具不備/製品失敗0、正式1964-53/個別17-190/工数null/QA051final/全F03-451/HOLD/原見積不変。群2/5/8cap10を保持し、N/T専有費null・共有消費を専有に割付けない。12680完成/群終了fresh枠/event・保存commitは456へ追補する。
