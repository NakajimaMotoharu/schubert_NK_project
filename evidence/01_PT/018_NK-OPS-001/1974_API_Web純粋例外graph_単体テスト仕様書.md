# API/Web純粋例外graph単体テスト仕様

2026-10-25、群PURE_API_WEB_FAILURE_GRAPH9_V1、sourcee598a81bb4200b4e4930278b31479ff927aa025f。原owner/costはAPI TemporaryInfrastructureException=P01805、Web WebStartupException=P01806、実行費は一群.5/2/6pp/cap10、component参照追加費0/実配賦不明。freshused12残88/reset1793513544。RD MQ006/008/OPS監視、UI231/251、SS312/324/342/354・SSC329330・元1430/1437/1439、PT-TEMP-GRAPH329001～003/API-STARTUP-GRAPH330001～003/WEB-STARTUP-GRAPH330001～003へ対応する。

対象Main二source unit全methodはconstructor/preserveFatal/attachSecondary。TestはTemporaryFailureGraph329Test3、ApiStartupGraph330Test3、WebStartupGraph330Test3の9件/3suite。Main二件/三Test/全nested helperを読取済み。新Main/Test/ID/fixture変更0。旧6566/6568の成功を当sourceへ転用せず、現normal9750全source/hash・元宣言9592のTest source/class byteだけを再利用し必要な選択試験を当sourceで実行する。元全4222の確認再演0。

独立期待値は1430/1437の固定表と当TestのassertSame/ArrayEquals/literal。直接Error→cause→suppressed→JMS linked→SQL nextのFIFO順、同一Throwableのidentity visitedによる混合cycle/重複edgeの有限帰還、後から追加したErrorの同一object伝播、元cause/suppressed/linked/next非破壊を確認する。null契約はNPE、未知の非fatal Throwable/空JMS・SQLは正常return。catalogはAPI literal request transaction is unavailable、Web fixture component PUBLICでPUBLIC is unavailable、cause null/suppressed0。attachSecondaryは同一objectへself-suppression0、別objectだけattach、suppression無効ではprimary graph優先→secondary graphの元Error、非fatalのみならreturn、両null境界拒否。provider graphを新catalogへ保持しない。

PT_DEFAULT：すべて自己所有memory上のThrowable/SQLException/JMSException/DisabledRuntime/DisabledErrorだけ。JMS/SQLは例外型であってConnection/Factory/DB/HTTPを開かない。Timeout5秒の独立JUnit thread、visited集合と有限fixtureだけを用いる。起動/readinessというclass名から実起動を実行せず、実Root/VM/cohort/停止/権限/permit/鍵/native/原本DB/Backup/私有raw操作0。新only slotはcompile-launcher/JUnit/report出力だけ、旧normalと原成功/失敗はread-only。拒否対象未特定範囲の再試行・境界探索ではない。

9772は厳密9宣言/3suite・当normal/source/Testclass byte/全2Mainを凍結し、9774は明示9methodだけ実行、9776は当XML/summary/session/CRCと二source unit全classの四counter/適用性を独立測定する。F/E/S/aborted/flaky/not-runを成功へ入れず、未網羅/0-counter/生成filter限界を分離する。旧exec union/除外/人工到達0。Main byteと型依存が不変の静的だけ9762/既六静的根拠へ参照し、別sourceの動的成功を合成しない。正式1964-53/17-190/工数null/QA051final/全actualHOLDは維持し、単位成功/commitだけで停止しない。
