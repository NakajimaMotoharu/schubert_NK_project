# MON006 監視27component寄与trace仕様

G13.07主/関連G13.04/05/06追加0、原0.5/2/5pp cap7。既112責務観測と原12明示84linkは再利用し、残100のうち固定570の27sourceだけをapproved RD MON006へsupporting-componentとして個別理由付きで結ぶ。JVM/GC/system9、DB pool9、heap4、disk2、HTTP latency3。明示code annotationとは別kindで記録し、実測・要件実装・PT・coverageの受入にしない。

根拠はRD171のMON006（JVM/heap/GC/DB pool/disk/HTTP response-time）、SS351の個別metric/標準SDK/health contracts、各Sourceの既責務宣言。命名だけからguessせず、各27責務原文と具体的な寄与点を570に事前凍結。既Source/Unit/collector/実backendを再演せず、unknown73は保持。

原WBS/112declared data/歴史source・費用・受入は不変更、別derived contributor overlayのみ追記。独立postは手書き27-nameとcategory、既pending membership/Source hash/原宣言/canonical requirement正文/authorityを確認し、要件全達成/実測/新Testへの誤変換、誤requirementや重複欠落を拒否。metadata-only source-reference品質であり100→73を工数率/実装機能完成率とは呼ばない。
