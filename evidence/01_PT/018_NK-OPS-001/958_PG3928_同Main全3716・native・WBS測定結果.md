# PG3928 同Main全3716・native・WBS測定結果

NK-OPS-001/NK-BAT-001、451/K01/G13、Main7fff/PG3748/BOM652915c6不変更。fixed snapshot **cb55caf0ce2b330880f63d717ba31270588847ff**、archive **cde4305d909b82962a93327bf35bf63565cc3a6f06f1622ea98c9dce87cecfdb**。PG3928元exec89619は03:44:02.551916～04:10:31.374481Z、真正actualExit/MavenExit0で終了。Root業務の30分budgetではなくhost全回帰の実時間として区別する。元3714＋956の独立Session2件をまとめた必要な一回integration、重複回帰/VM/配備/Root/Backup/ADMIN再演0。

| Test ID | 独立期待値/根拠 | 実結果 |
|---|---|---|
| PT-ALL-3928 | 原3714case集合＋実Session2識別子、全六module期待3716/545/1643、全scope入力固定/新XML・失敗再送skip無し | actual0、3716/545/1643、FESFlakyNotRun0/CompilerNullAwaySpotBugs六module0 |
| PT-ALL-3930 | 原begin/archive/全source/保存XML・元3714全case、全Main/resource/debug物理member | 独立actual0、全1643物理byte差0、全旧case保持、追加2のみ。qualification SHA d702987c3f486f4326af062dd98f478401d0020501059a90c70c67eaa1e32d54 |
| PT-NATIVE-3938 | 同7fffの元3892保持済み20point/18latestのみ、全blob/helper/library hash・旧新全1643物理同一・Inspector同session/単調/closingのみ・全CRC | actual0、18stream/20point、classByteMismatch0、foreignSource輸入0、VM read/再採取0。server SHA c9791d4c99b4134b06fc7d539e6ea4e8e94ce5fb3a1ec6b7e2e1bd63cd6f3682 |
| PT-NATIVE-3938-PURE | 143/別source/物理差/不足stream/foreign/未登録debug差を拒否、保持cache不変 | pure2成功。pure初期の未完成namespace coordinates欠落はTDD中に補足、実発行は完備後一回 |
| PT-WBS-3956 | 同source全941artifact/17受入・481/484 byte不変、現XML測定だけ更新、候補audit→journal→正本audit | pure2・stage0/apply0、未割当0、97counter閉鎖/18gaps、新受入leaf0、予算/主担当/元見積り不変 |

公開PG3954 manifest **60b36e321b16806b428b1948ca78374b27089f807f5b22abc2df7d22c70bf766**、六coverage XMLは技術session IDだけSHA256化し、counter/method/class/line/timestamp内容を不変照合。全物理Main SHA/各module XML・static hash/資格receipt hashを保持。元full server manifest **a4add111eb17b7330846420683911d2c848c8c92023000cb0d0781d3a50504e9**。実command/OS/JDKは元PG379/PG3928・3930・3938/各server manifestへ保存、固定JDK25.0.4/Maven3.9.12/JaCoCo0.8.15。秘密/raw session/DB/key/native本体公開0。

全体未網羅 **642行/128method/5class/459branch**、前642/128/5/462からbranchだけ**実3減**。bootstrap/protocol/storage/webは四counter miss0、api27行/1branch、batch615行/128method/5class/458branch。個別合格17/190・工数null・正式1964PT/53scope・QA051final保留、F03raw1840/技術304/未分類1536/適用違反null/F03未受入は維持。二実JUnit追加と管理pure/選択65再実行は二重加算しない。PGPT/ITST完了0。

BUG1329/YKT1095の元begin説明は旧Root/hygiene群のままというmetadata不備。元cb55 payload/beginは不変保全、3936外部訂正receiptで実Session2/Test一file変更・source/archiveを束縛し、将来生成文面はf50434ba9で是正・pure3。今回3930が旧case集合＋実Session2を別に検証し、3938/3956まで実source/counter整合を確認、数値/成績への誤認証がないことを閉鎖根拠とする。元runを書換えず再実行0。
