# FieldCodec NFC固定scalar・wire 実行結果

2422/群event2789、sourceb11fe71bd20e244dd10c83bd339f8345a0c1f085は新Test一つだけで全Main/旧Test不変更。新Hangul Jamo/Angstrom/結合文字順序の三caseと関連旧FieldCodecTest whole五、計8/二suiteが同一source/runで全成功。新unique IDは三、旧五/過去sourceの成功を加算又は移植しない。RD MQ-018/031/033・MSG-002/007/010、UI232§4/SS322§4.1/6.1/11の固定scalar/hexを独立期待とした。実DB/JMS/VM/Root/FFM/native/Graph9/鍵/業務IO0。

## 真正結果・独立証跡

各manifestはProgram018/evidence/provisional配下。実command/時刻/OS/JDK/source/branch/SDK/工具hashはbegin/invocation/stagesに保存、commandはchecked entryと対応Python名。JDK25.0.4/Maven3.9.12/JUnit1.13.4/JaCoCo0.8.15、専用JVM240秒/heap768/locale ja-JP。

| Run | SHA256 | 確認範囲 |
| --- | --- | --- |
| PG13152-nfc-golden-preflight-v1 | c7a2ac738655f537cc227ee88b16d89e163ef618c6698ba03ac0d5487f25c34e | 三Main/二Test静的PMD-CS0・新旧case/expected authorship |
| PG13154-nfc-golden-plan-v1 | 7695d1297c842faf24096b623194ff74903b849d58f2b4355f002ae9b5a5748f | 元whole5＋新whole3/三Main閉集合固定 |
| PG13156-nfc-golden-six-compile-v1 | 4c1f5352b5d048cda761851d3482fd74983b3ec885ed839d91f987bca60be0d9 | 六normal真正0/PT0 |
| PG13158-nfc-golden-host-v1 | 90af523f25fd27284d2fc5de6e2205ab1bfe0fcb4f77db7ae94f0d7e142fcabd | 全8真正0/FES-aborted-container失敗0/一session PG13158-NFCGOLD-JP |
| PG13160-nfc-golden-static-v1 | d5421c9de06fd99be43811f7f7faf32a9f963d4ae0b31d1bea24449c36c71ffd | 同hash事前PMD-CS再束縛・六SB0・再解析/製品再演0 |
| PG13164-nfc-golden-post-v2 | cdec2827b883dd6e6d75a9aecbe1fbc11f3d42ab36f7bccbfb6a6e9479d275ad | XML/一execCRC/全六artifact・全1843Main旧1973Test同byte/新一・厳密五Rootと型別分母 |
| PG13166-nfc-golden-trace-v1 | 3f8769ae62a70375d0d0a1b7e6085110d0dd9a08ec711be368b024f0392230e8 | 旧994全field＋新一ownerP00201、995row/Java1821登録1819/unknown二 |

入力/期待/実際は新3 TestIDで固定scalar/hexと実assertion成功を一意結合する。Hangul6/9byte表現は3byteへ合成後に上限判定、Angstrom3byteは2byteへ合成、qの結合順序は5byteのまま正規順へ。各NFC wireは正規scalarとpaddingに一致、元非NFC wireはPermanentProtocolException・入力array不変、送信上限未満はFieldEncodingException。expectedをproduction/JDK Normalizerから生成0。

## Coverage・制約

FieldCodecはline119/0・method15/0・class1/0・branch83/1 covered/missed。FieldEncodingExceptionとPermanentProtocolExceptionは各line4/0 method2/0 class1/0 branch0/0（branchなしを正の網羅実績へ加算しない）。当FieldCodecのbranch一未達を保持し四100ではない。全protocol/他五artifactも完全分母・未達を保存、全case/同exec/CRC・全Mainと旧Test byte一致・新一physical・唯一定義/全source/SDK/工具pre-post同hashを照合。空CWD/許可外Product probe0、runtime CPはprotocolだけ、他Mainはreport時のclass byte読取だけで初期化・実行しない。

BUG2034/YKT1782は初回13162末尾余分括弧による事前lint1/bodyStartedfalse。元entry21dfde90/失敗を保全、別13164は末尾一文字＋namespaceだけ是正、bind前pyflakes0/checked0/初回独立measurement成功。製品8/normal/静的再演0、工具不備一/製品不備0/追加source cycle0を元見積と分離する。PGPT全体/64layout/CHR/native/正式451/全G13は未受入、全WBS監査HOLD/正式1964PT53scope/歴史17-190/工数null/QA051final維持。raw8459/corr966/参照3271pending975は不変参照・全global再解析0/新raw追加0、unknown二を埋めない。原2/4/8cap10・開始共有4/reset1793774153・専有費/N/T/工数null不変更。
