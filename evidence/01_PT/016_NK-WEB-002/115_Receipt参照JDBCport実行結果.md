# Receipt参照 JDBC port実行結果

{
  "atJST": "2026-11-05T14:40:27.350792+09:00",
  "source": "52f67513a56e5d67dd32f85bd7b36a39e2ab0f55",
  "productionCoreMain": "b09393b0e746b55fd480176d57996d65bd76a95d",
  "run": "PG18888",
  "actualExit": 0,
  "tests": 9,
  "testClasses": 1,
  "FESaborted": [
    0,
    0,
    0,
    0
  ],
  "wholeSourceFourCounter100": {
    "dev/codex/schubert/nk/web/receipt/ReceiptReferenceRepository": {
      "INSTRUCTION": {
        "covered": 309,
        "missed": 0
      },
      "BRANCH": {
        "covered": 36,
        "missed": 0
      },
      "LINE": {
        "covered": 92,
        "missed": 0
      },
      "COMPLEXITY": {
        "covered": 27,
        "missed": 0
      },
      "METHOD": {
        "covered": 9,
        "missed": 0
      },
      "CLASS": {
        "covered": 1,
        "missed": 0
      }
    },
    "dev/codex/schubert/nk/web/receipt/ReceiptReferenceRepository$Work": {}
  },
  "physicalClasses": 2,
  "abstractInterfacesReported": 1,
  "heldFourProbeHits": {
    "dev/codex/schubert/nk/api/idempotency/ResponseSnapshotCodec": 0,
    "dev/codex/schubert/nk/api/idempotency/FingerprintKeyRing": 0,
    "dev/codex/schubert/nk/web/bootstrap/WebStartupException": 0,
    "dev/codex/schubert/nk/api/error/TemporaryInfrastructureException": 0
  },
  "manifest": "evidence/01_PT/016_NK-WEB-002/evidence/PG18888-receipt-jdbc-port-nine-v1/manifest.json",
  "manifestSha256": "d0b93fb970b246fa7af1cf5d4b5b6d220bc2b94ec12bdf28dc9bdcfb1102dd02",
  "environment": "evidence/01_PT/016_NK-WEB-002/evidence/PG18888-receipt-jdbc-port-nine-v1/environment.safe.json",
  "PG": "Main unchanged; literalSQL/independentTX/ownedcleanup reviewed 765/768/770; Test009 closes insertclose same declared exceptionprecedence",
  "independentOracle": "SS331/332 literal SQL/tuple and original rcpt005 exceptionselection; not production-generated",
  "static": "PG18886 raw29 per-finding applicability770; applicable0/CS0/parse0; Main NullAway and sixSB same input hash PG18642/18648",
  "originalRun": "PG18874 full8 success but 2L/2B missing, retained; producer/exec/result not rewritten or unioned",
  "faults": "BUG2282/YKT2027 equivalent Teststyle corrected; all9/static/post retested; publication commit pending",
  "limits": "No actual DB role/PK/isolation/IF025/native/Root/HTTP qualification. WBS-P01104 remains open, new accepted0/formal1964-53/effortnull unchanged",
  "technicalOriginalPartial80": {
    "wholeQualifiedComponents": 4,
    "notYetWholeBound": 76,
    "globalRegistryUpdated": false
  },
  "cost": {
    "originalStartEstimatePp": {
      "low": 1,
      "base": 3,
      "high": 7
    },
    "capPp": 10,
    "quotaAfter": {
      "primary": {
        "usedPercent": 14,
        "windowDurationMins": 10080,
        "resetsAt": 1794395640
      },
      "secondary": null,
      "usedPercent": 14,
      "remainingPercent": 86,
      "windowDurationMins": 10080,
      "resetsAt": 1794395640,
      "observedByJST": "2026-11-05 14:39:26 JST",
      "provenance": "fresh get_usage_limits direct structured response",
      "previousObservationSha256": "3e82a3f012ce63245eb0c3e0804ea5d773245ff98a7a64939456c0b0a81fbc0c"
    },
    "reportedSharedDifferencePp": 0,
    "zeroNotFree": true,
    "exclusiveActualAllocatedPp": null,
    "N": null,
    "T": null,
    "ordinaryClosedSharedPp": 8,
    "allRecordedSharedPp": 15,
    "SsharedPp": 7,
    "V": "samefirstHOLD no product acceptance, no second pilot"
  }
}

再現command（成功の確認目的で再実行しない）：`env PYTHONPATH=tools/quality python3 -B /home/mini/codex/project1/work/pgpt-runs/PG379/media_range_port_driver.py run receipt 52f67513a56e5d67dd32f85bd7b36a39e2ab0f55`。独立postは同引数の`post receipt`で終了0。実command/start/end/OS終了値は公開manifest/stage exit、TestID001～009は114とselectedTestMethodsで一意に対応。再現にはinput038、PG18884 compile/PG18886 static、正常Main PG18642 artifact pinが必要。


## BUG-3811の現候補再試験

製品 `8e2a6b055c45f9f868433c73174b87bc72972d77`、JDK代理同一fixture9/9、失敗・エラー・スキップ各0。直接のcloseとrollbackを保持し、cleanup時の失敗伝播を共通化した。原execで行104/104、メソッド10/10、実行コードクラス1/1、分岐32/32。Workはabstract、命令は352/373。先行是正ではSpotBugs資源所有3件が発生したため適用成績に算入しない。最終静的はNullAway・書式・Checkstyle 0、SpotBugs Low 1とPMD20は生出力・担当判断残。実DB、正式451は未了。 [PG44836/38](evidence/PG44836-receipt-cleanup-branch-specific-proof/manifest.json)

## PG44914 受付参照のNPE伝播

現候補の製品クラスはPG44838と同一。再現入力はJDBC interface内の合成ResultSetだけ。PT-WEB-RCPTPORT010は供給元と同一の例外、commit 0、行／文／rollback／接続の順を1回ずつ確認した。同一実行の元9件と新1件の計10件が成功し、失敗・エラー・skip・未実行は各0。現対象クラスの未加工coverageは行104、method10、class1、branch32で各未達0。別のexecは合算していない。現在のCheckstyleとGJFはこのfixture1件について終了0。型付き静的検査の新fixtureへの適用と実DB・全451は別。

[PG44914](evidence/PG44914-receipt-npe-owned-ten/manifest.json)

## PG44918 受付参照のJDBC時刻契約

PT-WEB-RCPTPORT011は固定の二つの非ゼロoffsetを同一Instantとして読取り、登録時の第3引数がUTC OffsetDateTimeであることを確認した。各読取・登録でcommitと所有接続closeは1回、rollbackは0回。同一execで元10件と新1件の全11件が成功した。対象クラスはPG44838と同一で、未加工の行104、method10、class1、branch32の未達は各0。実PostgreSQLのtimezone設定やドライバ動作は別。関連WBS-P004-05/2。

[PG44918](evidence/PG44918-receipt-offset-owned-eleven/manifest.json)
