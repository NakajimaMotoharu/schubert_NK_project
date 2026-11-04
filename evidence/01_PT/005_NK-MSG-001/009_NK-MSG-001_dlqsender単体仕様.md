# NK-MSG-001 DLQ Sender独立単体仕様

対象DlqSender全class/method、PT-JMS-DLQ001～008（新whole DlqSenderContractTest八method）。RD MQ008/010、UI231/232、SS312§9/321§7～11、PG-D017/018。674原見積0.75/2/5pp/cap10・普通477/478のまま。675で要求/独立期待・現Main依存と既成功再利用を先行凍結。original130vectorは保存し、初回compile前に127byte transport/35char UUID二欄/7char layout/count2の五境界を追加、最終予定135vector。新Test IDを135と数えず八件とする。

PG15616のWriter/MetadataとPG15520のGuardedは現Main6b53の独立資格を再利用、元九/六Testの確認目的再演0。旧OutboundJmsAdapterTest実broker fixture/methodへアクセス実行0。SDK値構築669を使い、自己所有JMS TextMessage/BytesMessage/Producer/Context proxyだけで実行する。全transitive Sourceは675で6b/Git/hash一致、Temp/WebStartup/Root/鍵/DB/実providerへ進まない。

DLQ001：opaque literal byte 00/20/ffをGuarded snapshotへ渡し、原配列変更後も同byte・十property・fixedDLQ/persistent2/TTL0をstage、borrowed context commit/rollback/close無し。これはcodec/有効業務wireの証明ではない。DLQ002：三API originの独立literal address/queue/DetectedByを使い、原TextMessage handleを保持、本文/型/deserialization/ack読取禁止、任意Password/BodyHash markerをclearしSS321十propertyだけを再設定、JMS replyTo/type headerをnull化。元bodyやObjectをreadしない（interface unknown callは即AssertionError）。

DLQ003：transport null/空/blank/space混在/127/128/129/ASCII0x1f・0x7f/0x7e/非ASCIIの11vector。上限128 printableASCIIは既qualified Writerの独立oracleを共用する。DLQ004：message/correlation各十境界（null/空/blank/canonical/大文字/零UUID/短縮表記/不正36/短35/過長37）計20。DLQ005：layout九境界（含7/8/9）＋count八境界（欠落/MIN/-1/0/1/2/4/MAX）計17。`UNAVAILABLE`はPG-D018既方針の診断sentinelで、正規wire IDではなく8/36幅から区別する。Unknown8char型適合layoutは診断保持としregistryの有効性を主張しない。countはJMS符号付きintの正値を保持、missing/less1は1、broker側max-delivery/ACKは別未検証。

DLQ006：trusted三null/untrusted四null/両非TX mode/二admin originの11vector、messageの読取・変更前拒否。DLQ007：25 API段階（Message20段階はchecked JMS/IllegalArgument/Error、Context/Producer五段階はruntime/Error）の70vectorを注入、同じThrowableと独立literal段階prefix・後続/再試行/commit無し。DLQ008：trusted write checked例外と129transportの二vectorをproducer送信前に拒否。fixture/input/fatal/Throwableはassert前に構築し、expectedはUI/SS/PG判断とliteral表から固定してProductionを使わない。getStringPropertyは二known key以外・本文/deserialization/ACKはproxyが拒否する。

実JDK25 javac/既存Consoleで当wholeclassのみ・並列/自動extension false・180秒有限、JaCoCo新session appendfalse/fullphysical DlqSender、元XML/FESaborted・classCRC/入力/終了を独立照合。四counter100と正常/異常/null/例外/境界の実証を要求し、不足/未実行は未完。PMD/Checkstyle/formatは同sourceで行う。全固定source/command/OS-JDK/tool/branch/終了/coverage/BUG/hashは010結果と公開manifestへ保存する。実JMS隔離/ACK/rollback原子性/native/CHR/全451/正式/IT-ST/Vは当unitだけで受入にしない。
