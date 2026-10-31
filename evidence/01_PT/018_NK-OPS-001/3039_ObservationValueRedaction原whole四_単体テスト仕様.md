# ObservationValueRedaction原whole四・単体テスト仕様

2026-10-31／PG-D971／NK-OPS-001、SS321/343SSC126130137・SS351§10.2/352§12/353、原PT-OPS-OBSDATA001～004・2343/2346承継。Production6b53/normal14216、HEAD559032fac070ed4da582e3a7744230605102d463・push27219真正0、freshfetch0/origin-main8b91944df不変。群3376実leafP01803.02開始0.5/1.5/3共有pp cap10、関連論理ownerP01803/P01710/P00307は追加費0。旧12530別source成功は歴史として保持し当sourceへ転用/確認再演しない。

原whole ObservationValueRedactionTest四/一suiteだけを選択、input/expect/bodyを変更しない。Test全文、原2343/2346、五record constructor/getter/toStringとそれぞれの外側static初期化関係を確認。Java nested recordのnewは外側classのnew/初期化ではない。実呼出しはServiceConfigFiles.Contents・RootReleaseAdmission.EffectiveConfigurations・RootServiceFacts.Facts・MorningBrokerExecution.Observations・BrokerJournalEvidence.Summary、既helperのArtemisStartupObservation.Evidence/StorageRootLayoutだけ。全record constructorはNullMarked契約/既Objects非null又は既定の素通し保持であり、DB/FFM/Root factoryへ進まない。Source外側業務メソッドは実行保留。Summaryの未規定null/値validation等の新契約を追加しない（2346どおり）。

- OBSDATA001：二public markerと二YAML/六lexical public roots、RootFactsのconfig/binding同identity保持・固定redacted text・null二。
- OBSDATA002：immutable nestedMap/Evidence/Summaryというfake情報だけ、BrokerObservationsの二同identity・固定redacted text・null二。実broker read/運転/permit資格ではない。
- OBSDATA003：別二public canary/固定三hexと六絶対path/YAMLがEffectiveConfigurations/Summaryの診断へ出ない。先行2346固定golden EffectiveConfigurations[non-secret=<redacted>]/BrokerJournalSummary[redacted]を使用、Production methodからexpectedを作らない。
- OBSDATA004：EffectiveConfigurations五field欠落とContents二欠落、全七NPE failfast。内部nonnull契約の確認で、NPEをcatchし業務成功へ正常化しない。

ファイル/crypto/network/JDBC/JMS/credential/Root/Unit/VM/actual observation/export/agent/native/実private dataアクセス0。Path.of/normalizeとJDK collectionsは字句/メモリだけ。外側ServiceConfigFiles.RETAINED_PRODUCTION（FFM/NioIo作成）、RootReleaseAdmission.create/inspect、RootServiceFacts.inspect、MorningBrokerExecution.execute、BrokerJournalEvidenceの実journal処理は呼ばない。これはunsafe wholeからの一部抽出や新代替fixtureではなく、元の独立四Testそのもの。実Root/拒否対象未特定範囲のHOLD解除0。

対象分母は五Source全部（RootFacts/MorningBroker/RootRelease/BrokerJournal/ServiceConfigFiles）の22physical、17Code＋実abstract interface五。呼ばれるnested Code五以外のCode十二は明示未実行として各全counter分母に含めcovered0、NoCode偽装/手動除外/公式filter変更0。Root外側五とNioIo等のtrueprobe0を同execで必須、四held六native境界も0。helper既Source資格を追加受入しない。全Source全100を期待/宣言せず、未達は結果3040へ保持する。

Command python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg15902_observation_public_values_four_pt.py。JDK25.0.4 freshjavac Java25/proc:none/Xlint/Werror・固定六Jar/外部依存、JUnit Jupiter5.13.4/Platform1.13.4/JaCoCo0.8.15・自己JVM180秒。Main五/Test一hash・二moduleJar全closureは当script固定、normal/source/snapshot/Jar byteを実行前照合。準備の単純metadata queryでhelper import用PYTHONPATH欠落はmain前に停止し、json-only queryへ整理、試験body・Source変更0。未実行/Failed/flaky/skipped/not-runをPASSにしない、障害は修正前915/916。正式1964/53/歴史17/190/工数null/QA051final/全HOLDを保持し通常小群で停止しない。
