# 1273 JMSowner取得前準備のPG/PT

Programs NK-ASY-001（Question）、NK-MSG-001（API WebLog/Web Reply）、NK-API-001（assembly）；UI212/213/231/243、SS312321342/411451/PG-D457、BUG1537/YKT1297。群1462開始0.5/2/6共有pp固定、全体原/v3/v4見積から完成控除しない。

原sourcec4/当148の実Jar（API/Web全classが6054全1667map一致）に対する6072actual0：三consumerのfactory.get/openはconstructor呼出より先で、そのcaller位置は全exception range外、ctor内でAtomicBoolean/lockをnewする。ApiMessagingRuntimeはdefault empty ArrayListへ最初の取得済Sync groupをaddし、そのgrow失敗時は未登録ownerをcatchが参照できない。公開manifest55bb9f0444535bfa0678b82abd0ff3543f46d62f54e7940f5102d7aaae5f9de2に各method codeSHA/offset/実allocation/元JarSHAを保持。これは独立したJVM順序のPG反例で、実heap枯渇/実broker漏洩のPTを実施したものではない。

JMSOWN001..003：各ownerの公開factoryに、取得前の独立IllegalStateException/AssertionError、null戻り、正常proxy contextを与える。未知failure同一性・取得一回・未取得close0/通知0、正常setup/listener/start・close一回・二度close非再試行を期待する。Expectedは固定call列/独立counter/Throwable identityから作り、Production helperで計算しない。既全consumer・API assembly/Web parentの正常/部分startup・fatal通知/close複合・null/並行/再送のfixtureを影響選択し、元successを新sourceへ輸入しない。

JMSOWN004：実新Main bytecodeで三ctorのowner/field allocationがfactory呼出より前に完了し、取得後は既nonnull確認/型cast/final context格納/returnだけ（new/newarray/anewarray/boxing/callback/未知call無し）であることを検査する。ApiMessagingRuntimeは容量3を取得前に構築し、固定最大三groupだけを順に登録、最後のowner/immutable copy失敗は既全group保護内であることを確認する。Sync capacity4/四contextの既登録とcallback順、WebBrokerContextsの別provider候補は個別横展開状態を保持する。静的順序確認を実行PT PASS/実測coverageへ加算しない。

原6060/sourcec4実行中はMain/Test/snapshot固定、原終端保全後にだけ実装する。通常PTは自己所有proxy/in-process broker/既temp DB・loopbackの明示fixtureだけ、VM/current/Root/原本DBBackup/鍵/failed-cohort/intent/permit/拒否再試行0。実施前にPTPREへsource/command/fixture/副作用/依存を登録し、clean commit/new-only runで一回実行する。四counter100%・型null/静的/全source物理差・公開ABIと必要全体/CHR/trace/451を別に判定し、未知未測定を100へ補完しない。元反例・新実行のsource/run/hash・実command/OS/JDK/tool version/終了を別結果へ保存する。
