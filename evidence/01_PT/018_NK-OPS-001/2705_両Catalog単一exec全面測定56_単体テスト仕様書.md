# 2705 両Catalogの単一exec全面測定仕様（既56case・新規件数0）

source6b53/dev-foundation/Gitbb1a0809eb0a8728e3a1c71237e025038c7ae23a、NK-OPS-001/RD171/UI252/SS351/PG-D917。PG14556/58、event3095 .5/2/4pp cap10、PT_DEFAULT/coverage未達閉鎖のための必要試験。原660methodへ新56を足さない。新Source数0、新TestID0。既616/660 registryと旧二未達測定は非改変保持する。

## 再実行の必要性と範囲

2679/14466の元Catalog14各はpublic labels(Meter.Id)を検査し、captured-name labels(String,List)は各L1/M1未達。2681/14472の元Scrape14各はcaptured-nameとprovider単一読取を独立assertするが、公的Meter.Id overloadは通らない。別execの足し算は禁止なので、二Catalog全Sourceの単一exec四counter資格は未完。この新全面証明を閉じるため、変更のない既四wholeを同一JVM/session/execへ組み合わせる。元成功確認だけの再演でも、拒否/実DB/graph等を別経路へ移したものでもない。元14×4のcase identityは660 registryに全件既存であることを独立確認する。

## 原仕様・独立oracle

2679/2681全文の固定期待/全body/fixture/副作用レビューを継承し、normal14216全input、旧二wrapperPINS、二元postの固定hashへ現byteを結合。対象Test832+962行、MainCatalog335行、Scrape54/五Exporter670/WebText60・recorders全依存は既全bodyレビュー済み、今回MainCatalog全文を再読。新入力・assertion・Main/Test/fixture変更0。

APICAT/WEBCAT001..014は16API/7WEB family・固定domain/768Inbox/51-13gauge/1750HTTP/36media・null/unknown/duplicate/mutable copy/finite64taskを独立固定SS/35route fixtureへ照合。APIPOL/SCRAPE001..014は900/2219sample・NaN51/13・手書CDF/未知mode/STD source read0/borrowed lifecycle/故障identity/partial返却0・captured name/tag/value一回読取/Tag変更隔離を独立assert。期待をProduction methodから作らず、到達のためだけの無意味呼出しを追加しない。

自己SDK/NoopMeter/MockClock/自己4thread64taskと10秒期限/メモリ内Prometheus writerだけ。35route public resource読取のみ、実HTTP/network/server/JMS/DB/VM/Root/cohort/graph classifier/鍵/実data0。既held工具はmetadata前除外のまま。

## 検証・記録

checked Python entry14556で原56/4を新一exec一回、14558で全XML/元660の既case集合・原環境/全input/Jar・一CRC・二Catalog全physicalを独立検証。不足があれば未達維持し、別exec合成や任意除外をしない。元測定L1/M1は旧証拠として保持、新測定を置換候補として別追記。ProductJVMは一つ追加だがunique case数/Source数の増分は0。registry上の初回31execとは、全面資格用追加exec1を別軸にする。

normal14216/static14224・JDK25.0.4/Platform1.13.4/JaCoCo0.8.15依存とcommand/exit/日時/source/input/outputhashは各manifest。結果2706へ。独立postは旧660 registry7887147f、旧Catalogpost67ea369c、旧Scrapeposteddfd120へ束縛し、新unique0/二target上書き無しを確認。全formal1964/53/工数null/全F03-451/QA051final/HOLD不変。
