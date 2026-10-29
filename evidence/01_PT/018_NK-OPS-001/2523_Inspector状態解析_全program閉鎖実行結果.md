# 2523 Inspector状態解析 全program閉鎖実行結果

2026-10-29、2522/PG-D826/event2903～、source0061d178cda80c2ce3926290619c64db125dbcfc（初候補23582とは別）。当sourceの全23method/3suiteを一exec/一sessionで独立照合し、完全InspectorUnitSnapshot＋Target二physicalの四counterを閉鎖した。正式1964PT/53scope、個別17/190、工数null・QA051finalは変えない。

|工程|元manifest SHA-256 / 結果|
|---|---|
|PG13832 六compile/format/null/testCompile・PT0|8a3edc7a98ac32ea75ccf981dd38ee144159a8d0372bdd90922d6312a2219f65 / exit0。新normal、旧buildの成功転用0。|
|PG13834 三Test PMD/Checkstyle|3a997d5dda6cd81721cd3ccd1c99b3b0ab1490ce0e4f8ddf76820b272cf4ad4c / 計測処理0、PMD原exit4/raw2（旧有限poolのDoNotUseThreads二件を保持）、Checkstyle0。新重複警告1は消失、抑制0・全F03静的PASSではない。|
|PG13836 六Main fresh SpotBugs|d86e16c1bb83153cc7dae1d2fd174dbcce81c389611c1561ee740ba3fd518127 / Max/Low・全1843、指摘/MissingClass/解析Error0。|
|PG13838 上記独立post|7625ceb8d6f774482934ab5133973ef3adfbb1cf9af21483a12339b396f58c51 / 原六XML/全物理集合/現aux/八typed反例、再解析0・exit0。|
|PG13840 全源/byte/alias独立post|4f49a8c05ab699b13f46c6d6f77637437e8cf769393eb34cbc97faf32f9e09f6 / Main1843全byte不変、Test1978中当outer一physicalだけ変更。全四literal参照→一private定数の逆変換と四負例、原九＋新一method保持・exit0。|
|PG13842 原JUnit/JaCoCo|359d5072f939f002cc939a606fc762f95fd25e2227a078967ad66df94f112288 / javac/JVM/body0、23/3、失敗・error・skip・abort・container失敗0。新ID1＋既22を分離、loopは件数へ加算0。|
|PG13844 独立全program post|1765e226fef6761d6d975a535300e709c09f81e713e83974a567d309f671c113 / 原XML/全源・Jar/fixture/八反例/単一session/CRC差0、全scopeのline222/method34/class2/branch320、全miss0・gate0。|

上記manifestはすべて `evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG<番号>-snapshot-program-…/manifest.json` に保存（13832=six-compile、13834=test-static、13836/13838=PG番号-snapshot-program-v1、13840=source-post、13842=whole-pt、13844=whole-post）。command/実時刻/OS/JDK25.0.4・Maven3.9.12/JUnit1.13.4/JaCoCo0.8.15/toolとSDKhash/branch/qualificationHEAD/source・入力・期待actual/終了/元XML/counter/exec/CRCを原manifestと固定工具へ結合する。曖昧な短縮pathを唯一の根拠にせず、下記traceは実在path/hashを記録する。

13842 entry81b5def8…・13844 entry2b915b23…、session PG13842-SNAPSHOT-PROGRAM-WHOLE23。対象Main/Targetはcomplete source unitであり、Probe/Root cycle/nativeの一部を除外して全体100としたものではない。Artemis004は固定公開snapshot内artemis.service（SHA1b8fe8ea…）と明示memory Readerのみ、実manager/Unit/Root/DB/鍵/permit/VM/Graph9等0。373byte goldenは元/own-copy同hash。自己CWDの3行scalar traceはpost初hash（原終端hashなし）という限界を保持する。

BUG2080/YKT1828の再試験範囲は当四参照/一宣言・逆変換/元九assert/新境界・当23と新静的警告消失だけ。元13814/raw3・13812/16/18成功と13820lint1/body未開始を保全、13821は独立新entryでの元source byte確認。動的失敗0/試験再起動0、compile/static二source分は新診断是正に伴う手戻りとして記録し、旧sourceのPT成功を新sourceへ移していない。開始2/5/8cap10は変更しない。tool管理表示TypeError一件とprebody lint一件を製品不具合へ混ぜない。

全program技術閉鎖とleaf終了依存/全451は別。current source/rangeのtrace/全995旧runtime・原WBS予算/受入不変・限定公開保存とpushを続ける。既threads二件や未分類global/全actualHOLDを0に置換せず、通常区切りで停止しない。

### 追跡・原予算の独立照合

PG13846-snapshot-program-trace-v1/manifest.json SHA f075dc40f990fb89f449d6da6a58d50dd4a129cb2bc2b619f30d7d3b51d8c107、PG13848-snapshot-program-trace-post-v1/manifest.json SHA f6d3e0fda18dbdcaba8ee8c2c5b982d063538948defc0fdc2615f283faf0df86、真正0。全995rowの担当/費用/旧runtime全fieldを保持し、当Test SHA一fieldだけ新sourceへ更新。新限定23/四100を別currentQualificationへ記録、旧current qualificationは歴史参照へ隔離する。原941logical/943physical/予算/受入は不変、前後WBS audit1/HOLDを保持し、八typed反例を独立照合。485 SHA2e7740f742ea117c364acb981423a40e31d304adc3b10304ebf20ec993656b0b、486 SHA29738f891143f5f943bc3ad22e8cba96095fe2e670ef4ab12e397a9c6a3f3ccb。

既catalog導出raw6247/Main1491/Test4756/correction3194/refs3394/pending2533/noRef2853は変化なし（当sourceの全域再計測ではない）。fresh共有は開始31→終了31/同reset1793774153の丸め差0ppであり費用0の証明ではない。専有費・N/T・工数/残工数null、usage13222ba3（09:48:13JST、前cursor6a4a10d9、explicit0/完全性未証明）。BUG2080/YKT1828は当四参照の限定是正・検証まで完了、全global/実Rootの認定へ広げない。次は未検証whole候補の既後続/source/実副作用を照合し、独立通常PG/PTを継続する。
