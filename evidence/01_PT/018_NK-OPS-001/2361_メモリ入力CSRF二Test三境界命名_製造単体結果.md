# メモリ入力・CSRF二Test：限定PG/PT結果

2026-10-28 / source915a8ed153b00d76a80164d36f9ce5b86d645046 / PG-D750 / BUG1988-YKT1736。2360の三int/三ifのみ同値命名、原全eight/helper/期待値のtoken逆と11非同値反例が成功（12616/82e5f936）。Main/POM/全設定・他Test変更0、新TestID0。旧成功確認だけの再演ではなく当変更sourceの影響全二Testを一回検証した。

## 実行

入口は各 `python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/<entry>.py`（実argv/hashはmanifest）。TC421既定JDK25.0.4/Maven3.9.12/JUnit5.13.4-platform1.13.4/JaCoCo0.8.15/PMD7.28-record1298/Checkstyle14.3、OSと全jar hash/開始終了時刻は原stageへ結合。

- PG12618六正常 compile/package：967ad00d、session27958真正0/PT0/六jar、normalはsource literal `915a8ed15`を原文保持。ホストのgit rev-parseがfull915a8ed153b00d76a80164d36f9ce5b86d645046へ一意解決、同archive/snapshotの全input hash・git差分0を前後照合。短縮記録を別source成功へ読み替えず、この対応をhost beginに明示した。再compile0。
- PG12620 whole原8/二suite：42a5c55b、session18143真正0/F-E-S-aborted0、一exec PG12620-MEMORYBOUNDARY-JP・ja-JP/JST/空CWD。Inspector193..196各4＋CSRF032..035各4、全methodがXMLとexactcatalogで一致。Bootstrap tests.jarは自己testdirとの重複定義を避けCPから明示除去し、二Testと二Mainの唯一解決・全dependency byteを前後検査、テスト対象を除外したのではない。
- PG12622静的：d4cf88fc、session1650真正1/PMD九→六DoNotUseThreads、Checkstyle0/processing0。三AvoidLiteralsInIfConditionだけ是正し、残六を抑止して0としない。
- PG12624独立post：38a996b5、session66741真正0、XML・一execCRC/session/全Main1843byte不変更・三physicalTest差（FixedRandom debug含む）/他1959同byte。二outerTestのrawCode表現差はconstant-pool index差も含み得るため「同Code」とせず、意味同値は全token逆＋固定独立期待値と実8で別検証。FixedRandom rawCode同/debug差、独立reader3正常4異常。許可外Product probe0・JDBC/Artemis class load0・CWD空・全input/dependency同byte。

## 実測coverageと限界

InspectorDbCredential37L/6M/1C/28B、WebCsrfToken27L/8M/1C/8B。二Main計64L/14M/2C/36B、四counterいずれもmiss0。Record/enum除外追加・手動除外・旧exec unionなし。この二Mainだけの技術100%で全module/全F03/451を100%としない。

完全bootstrap117physicalのcounterはcovered37L/6M/1C/28Bに対しmissed3076L/607M/81C/1759B、完全web358physicalはcovered27L/8M/1C/8Bに対しmissed9903L/1804M/319C/3596B。package-info metadataも全数照合し分母から勝手に除外せず、JaCoCo既定filterは変更していない。旧Main/runtime/native成功は当sourceへ合算0。

PG12626 context28a41111／12628独立8e70e55eは六原IDの全XML座標・method/control・現在8件へ結合、22非同値反例0。Inspector自己pool12・CSRF自己pool10の100callbackと5/20秒get、finally消去/TWR、invokeAll/TWRの局所無期限・外側240秒の区別を保持。六historical refのsource再束縛で新分類0、六raw保持/pendingへ戻す。

PG12630 trace8a5d4b2f／12631独立7d9957a4、原983行の二SHAだけ変更・他981不変更、canonical owner/cost P01801/P01502/原budget/acceptanceを維持。全WBS前後は同じHOLD1、成功へ変換しない。PG12632 delta da59b0c8／12634独立5bd2474e、原三IDのみ是正・九非同値反例0、raw8504/累計913/Main1506-Test6998、追加8保持、refs3175/pending780/noRef5329。fresh全体静的解析ではなく実deltaの導出、actualViolationCountnull。

## 未完・費用

実credential/DB/HTTP/Root/Unit/Graph9/FFM/VM/native/permit/intent/Backup操作0。原本/保留二工具/stash七等の保全を維持。原通知は消失というQA053回答を継承し再要求しない。正式1964PT/53scope・個別17/190・QA051final保留・工数率null、全F03/451/CHR・実経路の未受入は不変。

群開始2/5/8cap10は固定、共有枠とN/T/専有費を分け、共有丸め差0を専有費0としない。新しいPT失敗/実装済み工具不備0。補助工具draft生成の事前guard一（存在しない置換候補へのassert）はfile作成/bind前に後続を停止、限定是正後だけ作成した。正常compile manifestのsource短縮表記は原byteを保ちfull hashへ一意認証し、同じ成功を再実行していない。群終了fresh枠・event・保存commitは456へ追補する。
