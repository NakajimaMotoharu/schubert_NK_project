# Expiry監査SQL・状態契約 単体結果

{
  "atJST": "2026-11-05T17:10:20.852937+09:00",
  "source": "d9e973756446d922bf1b2525f797ed8394c45bcb",
  "productionCoreMain": "b09393b0e746b55fd480176d57996d65bd76a95d",
  "run": "PG19028",
  "actualExit": 0,
  "tests": 38,
  "testClasses": 3,
  "failures": 0,
  "errors": 0,
  "skipped": 0,
  "aborted": 0,
  "coverage": {
    "dev/codex/schubert/nk/batch/repository/ExpiryAuditRepository$JdbcRelease": {},
    "dev/codex/schubert/nk/batch/repository/ExpiryAuditRepository$Prior": {
      "INSTRUCTION": {
        "covered": 15,
        "missed": 0
      },
      "LINE": {
        "covered": 4,
        "missed": 0
      },
      "COMPLEXITY": {
        "covered": 1,
        "missed": 0
      },
      "METHOD": {
        "covered": 1,
        "missed": 0
      },
      "CLASS": {
        "covered": 1,
        "missed": 0
      }
    },
    "dev/codex/schubert/nk/batch/repository/ExpiryAuditRepository$JdbcAcquire": {},
    "dev/codex/schubert/nk/batch/repository/ExpiryAuditRepository$Snapshot": {
      "INSTRUCTION": {
        "covered": 38,
        "missed": 0
      },
      "LINE": {
        "covered": 2,
        "missed": 0
      },
      "COMPLEXITY": {
        "covered": 2,
        "missed": 0
      },
      "METHOD": {
        "covered": 2,
        "missed": 0
      },
      "CLASS": {
        "covered": 1,
        "missed": 0
      }
    },
    "dev/codex/schubert/nk/batch/repository/ExpiryAuditRepository$Stage": {
      "INSTRUCTION": {
        "covered": 42,
        "missed": 0
      },
      "BRANCH": {
        "covered": 8,
        "missed": 0
      },
      "LINE": {
        "covered": 6,
        "missed": 0
      },
      "COMPLEXITY": {
        "covered": 6,
        "missed": 0
      },
      "METHOD": {
        "covered": 2,
        "missed": 0
      },
      "CLASS": {
        "covered": 1,
        "missed": 0
      }
    },
    "dev/codex/schubert/nk/batch/repository/ExpiryAuditRepository$JdbcRead": {},
    "dev/codex/schubert/nk/batch/repository/ExpiryAuditRepository": {
      "INSTRUCTION": {
        "covered": 1163,
        "missed": 0
      },
      "BRANCH": {
        "covered": 180,
        "missed": 0
      },
      "LINE": {
        "covered": 239,
        "missed": 0
      },
      "COMPLEXITY": {
        "covered": 110,
        "missed": 0
      },
      "METHOD": {
        "covered": 20,
        "missed": 0
      },
      "CLASS": {
        "covered": 1,
        "missed": 0
      }
    }
  },
  "physical": 7,
  "executableClasses": 4,
  "abstractInterfacesReported": 3,
  "heldFourProbeHits": {
    "dev/codex/schubert/nk/api/error/TemporaryInfrastructureException": 0,
    "dev/codex/schubert/nk/api/idempotency/ResponseSnapshotCodec": 0,
    "dev/codex/schubert/nk/web/bootstrap/WebStartupException": 0,
    "dev/codex/schubert/nk/api/idempotency/FingerprintKeyRing": 0
  },
  "manifest": "evidence/01_PT/017_NK-BAT-001/evidence/PG19028-expiry-audit-port-thirtyeight-v1/manifest.json",
  "manifestSha256": "70bac0cea88b28114415e98e669b08e571887f6b96c7dd43b3ff3ab0e7e1c2d9",
  "environmentSha256": "00bba679994d4e25b86e3a9b308b15260c068092b37e735fac45e0cc80738d6d",
  "initializationSupplementSha256": "25c9237d89fad5daff547d955ef6bafa08b856fd468d71f98effbca18edd5da5",
  "baseline80SamePathHash": true,
  "PG": "Main unchanged; V022stage/finish/read/retainedsuccess/nullabletriples/25methods fullreview, callbackpositiveGuard only, no realparent. IndependentliteralSQL/binds/counterclock/lateidentityloss andonefieldpredicatevectors, existing24TWR oracle preserved",
  "oracle": "SS331V022 fixedUTC-JST/3before2target1after200bytes, literalfiveSQL/timeout5/allbinds, independentstate/matchmatrices +Java25 TWR reference; no productioncomputedexpected",
  "static": "PG19022raw23 eachNA800, applicable0/CS0/parser0, normal6MainbuildNullAway/SBPG18642-18648 sameb093 fullinputs/jars reused; BootstrapGuard andJSpecify1.0.1 pinned, no additionaltool",
  "originals": "PG19016/19018 draftcompile0/raw23 preserved, beforefirstexecution WARNINGknownafter +lateidentityloss added PG19020/19022; initialpatchguard1 beforewrite/existingprepareguard1 beforecompile blockedduplicate, no failedproductPT",
  "oldExecUnion": false,
  "actualFrameStorageNativeDbRootVmBrokerOrOriginalAccess": false,
  "limitations": "not realDBschema/role/durableaudit/purge/retainedoriginal/actualowner/deadline/Root/native/parentWBS/V/451",
  "formalUpdated": false,
  "newAccepted": 0,
  "effortRate": null,
  "originalPartial80": {
    "wholeTechnical": 11,
    "notYetWholeBound": 69,
    "globalRegistryChanged": false
  },
  "cost": {
    "startEstimatePp": {
      "low": 1,
      "base": 4,
      "high": 8
    },
    "capPp": 10,
    "quotaAfter": {
      "primary": {
        "usedPercent": 16,
        "windowDurationMins": 10080,
        "resetsAt": 1794395640
      },
      "secondary": null,
      "usedPercent": 16,
      "remainingPercent": 84,
      "windowDurationMins": 10080,
      "resetsAt": 1794395640,
      "observedAtUTC": "2026-11-05T08:09:01.047Z",
      "observedByJST": "2026-11-05 17:09:01 JST",
      "provenance": "fresh get_usage_limits direct structured response",
      "previousObservationSha256": "bc372602bb6d2a3f935b274bd652ca0e88055c301770dde708e548bac1d9804d"
    },
    "freshAfterPostGuard": true,
    "actualAllocatedPp": null,
    "N": null,
    "T": null
  }
}

697のP001～005/J001～009と既EXP4956001～024は38selectedTestMethods/元XMLで一意対応。時刻/実argv/OS終了はstage exit、環境は元XMLhash確認後whitelist抽出。再現（確認目的の反復なし）：`env PYTHONPATH=tools/quality python3 -B /home/mini/codex/project1/work/pgpt-runs/PG379/media_range_port_driver.py run expiry d9e973756446d922bf1b2525f797ed8394c45bcb`と同sourceの`post expiry`。input697/PG19020compile/PG19022static/正常Batch-Bootstrap-Protocoljar/JSpecify1.0.1等pinsが必要。7physicalを全報告、宣言interface3はexecutable counter非適用でcoverageの0実測に偽装しない。
