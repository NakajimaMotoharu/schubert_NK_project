# Main局所Map四件・静的適用性レビュー

F03-MAINMAP001/PG-D732。開始save7edd5d08a6e590ecbc9dac493202ca552dd4e5a7/push21968真正0、source d8a2b7952b321b75fe7fcc1c8d3acb287faca6ec。主F03・原owner/cost追加配賦0、正式source照合/判断の着手前0.5/1/2週次pp・cap10。選定の四Main全文読取はGROUP_START前の調査として区別し、実token/専有費/時間配賦は不明null。fresh共有57残43/reset1793599188、旧見積/正式1964-53/個別17-190/工数null/QA051final不変更。

対象PMD00122 AssetChecksumManifest.read（SS333/343/UI237/243/NK-MED-001）、PMD07323 MediaRangeService.respond（SS311/333/UI223/235/237）、PMD03094 MaintenanceStopSnapshot.parse（SS341/343/SSC100/126）、PMD03111 MaintenanceUnitStopPolicy.parse（SS341/342/SSC101）。各UseConcurrentHashMapは「concurrent accessがある場合」の規則。HashMapが呼出し毎のlocalであること、可変参照が共有field/外部へ逃げず、immutable copyか検査終了で寿命を閉じることを全文・明示method/spanから確認する。Collections型を機械的に置換して契約を変えない。

独立確認点：Asset private constructorのthis.hashes=Map.copyOf(hashes)とread内唯一のnew HashMap、private addLineの単なるputIfAbsent、公開後はget/sizeのみ。Mediaはrespond毎にnew HashMapしresponse.beginへMap.copyOf(headers)だけを渡し可変headersを保持しない。Snapshotはparse localとthis.fields=Map.copyOf(fields)、公開getter/observedValues/matchesはimmutable String/enumの読取のみ。StopPolicyはprivate parse local四key検査でMapを返さず、fieldはSourceだけ。現SourceSHA/元row/現span/whole method/原artifact owner-costを固定し、別source・誤span・不変化根拠欠落・mutable逃避・実PT偽装などmetadata反例で独立照合する。raw四件は保持し全current適用性判定待ち。

新PG code変更不要という限定判断であり、静的reviewを実行PTのPASSや実測coverageへ混ぜない。Assetのみ既実12226/12230の同source med044並行100/borrowed channel・immutable result/CRC二Main miss0を参照し、新試験を再実行しない。他三は新PT/coverage資格なし。正常六12224は現sourceのbyte照合用、原10690 findingsは現四Main同byteのraw根拠として再利用し、全static再演0。Main/Source/Test/SSの書換0、全体WBS監査は前後HOLD維持。

485は原owner/cost参照の正本とし、Assetの歴史artifact SHA277695adと現source503f89c2を分ける。歴史SHAを現実装の証拠に使わず、current sourceは12224入力と現byteで認証する。残trace/品質受入は未完。他三のMainにはNativeSource等の実操作もあるが、当レビューはlocal Mapだけでcreate/requireSafe/native reader/systemctl/Root/stop/Unit/VM/DB/Backup/permit/鍵を呼ばない。Graph9/保留二工具・既stash/原本/Current/native/成功失敗を保全する。

予定12246 source四理由/12248独立metadata、現集合への四参照追加と原owner/cost/全WBS不変確認、公開scan/exact保存。受入増分0・ProductPT0・raw是正増分0、refs増分と工数完成率を混同しない。通常小群で停止せず次の独立PG/PTへ進む。
