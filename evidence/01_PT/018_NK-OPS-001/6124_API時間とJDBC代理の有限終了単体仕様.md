# API時間とJDBC代理の有限終了

NK-OPS-001、SS351/354、WBS-F03/2-2-b、BUG-3978／YKT-2997。DBCONN007は固定64 Observationと二owner・独立時間集計・既5秒のfuture取得を保持し、ExecutorServiceの暗黙無期限closeから既有限所有へ移行する。ASYNCDB008は64の独立JDK代理ステート、SQL後条件と借用所有、時間10秒を維持し、一次失敗をfinallyの失敗で置換しない。

両試験の経路は合成SDK・自己Connection代理に限定。006の実JVM計器、実DB・HTTP・JMSは対象外。現製品・選択fixture・独立期待・coverageの同一runと未成立をmanifestへ保存。
