# PG3934 Session境界PT：既存WBS子への対応追補

PMO-20261016-1344-BOUNDARY-CHILD-MAPPINGを受けた分類・計測追補。新規試験/署名/配備/VM再実行・新規leaf/受入/費用0。旧events0983～0988とcompile/oracle失敗、親/子の原予算は変更しない。以下の7fff資格を現在の7bb Mainへ転用しない。

| 元作業群/Test ID | 唯一の既存費用leaf/criteria | 独立根拠/原証跡 |
|---|---|---|
| P018_ABANDONED_REQUEST_BOUNDARY（0983開始P018誤記→0984親P017訂正、0985実64完了）/PT-MDB-3920-001 | **WBS-P017-01.03**「原本/JDBC/lock例外・close・資源後条件」。.03:deliverableの保持原本run/start境界拒否、.03:qualityの原値・lock・close後資源0に部分対応 | Source7fff、Test7c193f7d5f4698b869605b8e7806a085ac0aa886、TestSHA76347e3b4f5f64949599ab0a188a59b45e37eaf9ce0316361621fde806059d09。PG3934/PG3922/tests.xml SHA90848aac112bdbe22a095ea798b0234dc808e5b75a0c3769a06d839b18a83969。DB全行JSON同値/4行literal、別run/start拒否と正規cutoff受理、advisory保持/終了client・advisory0 |
| P017_FAILED_PAIR_METRIC_BOUNDARY（0986開始/0987新oracle失敗/0988実65完了）/PT-MDB-3924-001 | 同じ唯一leaf **WBS-P017-01.03**。.03:deliverableの異なる失敗pairを原本能力へ変換しないこと、.03:qualityの独立SQL counts/原値・lock・終了資源0に部分対応 | Source7fff、Test746ca85f876c4d3f0ebc0c6347710342481a4e8f、TestSHA4dd2c8ce546be96a13013850e098fb5af8b6b3e53749ec6dbf18eb0543a3bf9a。PG3934/PG3926/tests.xml SHA5a5ba08eb261e2ddda13e70aa3c5e7740c01c348cf53b7377c0115bcf795f73b。左右1/2二vector/同一失敗projection拒否、固定例外cause null/SQL非更新 |

原本/JDBC状態に固有のboundaryなので.03を主担当とする。.01正常owner取得/解放は事前条件・参照証拠、.02同時owner/再入/失効は今回全範囲を試験しておらず、費用/新受入0。親P017-01も階層alias/集約参照で二重費0。.03は依存.02が未受入・当leaf全範囲未照合なのでNOT_ACCEPTEDのまま。これら2境界の部分証拠からchild全criteria終了を宣言しない。

原群開始見積りはそれぞれ**.2/.8/2.5pp**、**.1/.4/1.5pp**を維持し、既leaf.03の内部stageとして対応付ける。別途leaf/親予算へ加算0、実費未分離actualAllocatedPp=null/N/T=null。stage見積り合計を実費やchild残予算減へ換算しない。P018誤記と二つの失敗（3920 launcher compile/BUG1328、3924新oracleのSS343/SSC124訂正）は元記録のまま追跡する。

PG3954は旧Source7fffの**3716/545/1643**統合（snapshotcb55caf0ce2b330880f63d717ba31270588847ff、manifest60b36e321b16806b428b1948ca78374b27089f807f5b22abc2df7d22c70bf766）。64・65は同じSession suiteの時点差であり3716へ再加算しない。K01は一回の統合実行/独立検証費だけ、境界実装・共通PT費を重複配賦0。956/958、PG3934 manifest a4634ff2に一意追跡する。

0980開始 **G13_CURRENT_7FFF_WBS_REVALIDATION / WBS-G13.07** と0982の親G13表記は**同一群の開始/完了alias**。元.3/1.2/4ppを一つだけ保持、新費用0。実3912/3914/3916/3918/955は既17/51criteria・941artifactの旧7fff再認証で、新製造leaf0/正式更新0。親G13やK01へ再計上しない。

新しいPriorExpiry群0995も親P017-07の表記を階層aliasとし、既存**P017-07.02**の公開request/原本identity境界に固有の限定PTへ対応（960）。.01/.03・親07は参照費0、同群.2/.6/2ppを一度だけ保持。子の全SQL/資源/原本保護範囲が完了したとの加点は行わない。
