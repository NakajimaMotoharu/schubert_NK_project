# Command metadata非null・非表示 単体結果

{
  "atJST": "2026-11-05T16:21:06.773427+09:00",
  "source": "f85525d010e5bf9af763cf584588921d0d0a1068",
  "productionCoreMain": "b09393b0e746b55fd480176d57996d65bd76a95d",
  "run": "PG19008",
  "actualExit": 0,
  "tests": 5,
  "testClasses": 2,
  "failures": 0,
  "errors": 0,
  "skipped": 0,
  "aborted": 0,
  "coverage": {
    "dev/codex/schubert/nk/api/application/question/QuestionCommandMetadata": {
      "INSTRUCTION": {
        "covered": 44,
        "missed": 0
      },
      "BRANCH": {
        "covered": 4,
        "missed": 0
      },
      "LINE": {
        "covered": 9,
        "missed": 0
      },
      "COMPLEXITY": {
        "covered": 4,
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
    }
  },
  "physical": 1,
  "heldFourProbeHits": {
    "dev/codex/schubert/nk/api/idempotency/ResponseSnapshotCodec": 0,
    "dev/codex/schubert/nk/web/bootstrap/WebStartupException": 0,
    "dev/codex/schubert/nk/api/idempotency/FingerprintKeyRing": 0,
    "dev/codex/schubert/nk/api/error/TemporaryInfrastructureException": 0
  },
  "manifest": "evidence/01_PT/011_NK-QST-001/evidence/PG19008-command-metadata-five-v1/manifest.json",
  "manifestSha256": "71543524b2ed3d184638aaa4bc1c3cf4329673b73f1f3e8d747d2bae0e791f66",
  "environmentSha256": "2b32ee9acac2203302100364ae0d1c49844de1d1781b196823f4f92f6fec815c",
  "baseline80SamePathHash": true,
  "PG": "Main unchanged; nonnullconstructor inputs/year0001-9999/UTCfloorµs/closedredaction distincttrace values; smallordinarycomponent notV",
  "oracle": "independentliteralUTC/UUID/fieldnames/exactredaction string, notproductioncomputedexpected",
  "static": "PG19002 PMD0/CS0/parser0/applicable0, Main6buildNullAway/SBPG18642-18648 sameb093 allinputs/JARpins reused",
  "oldExecUnion": false,
  "actualBackendResourceOperations": false,
  "limits": "not commandbusinessprocessing/DB/owner/token/HMAC/notification/parentWBS/V/451",
  "formalUpdated": false,
  "newAccepted": 0,
  "effortRate": null,
  "originalPartial80": {
    "wholeTechnical": 10,
    "notYetWholeBound": 70,
    "globalRegistryChanged": false
  },
  "cost": {
    "startEstimatePp": {
      "low": 0.25,
      "base": 0.75,
      "high": 2
    },
    "capPp": 5,
    "quotaAfter": {
      "primary": {
        "usedPercent": 15,
        "windowDurationMins": 10080,
        "resetsAt": 1794395640
      },
      "secondary": null,
      "usedPercent": 15,
      "remainingPercent": 85,
      "windowDurationMins": 10080,
      "resetsAt": 1794395640,
      "observedAtUTC": "2026-11-05T07:17:01.835Z",
      "observedByJST": "2026-11-05 16:17:01 JST",
      "provenance": "fresh get_usage_limits direct structured response",
      "previousObservationSha256": "fdfbca4c7c97ef6b2de08cb1449248c628825e4f5b23244c305e1b50cb20d98d"
    },
    "afterPostTimeGuard": true,
    "actualAllocatedPp": null,
    "N": null,
    "T": null,
    "sharedPp": 0,
    "zeroNotFree": true
  }
}

011のMETA001～002と既TIMEBOUND001～003は全5selectedTestMethods/元XMLで一意対応。実時刻/argv/OS終了値はstage exit。再現（成功確認だけの反復なし）：`env PYTHONPATH=tools/quality python3 -B /home/mini/codex/project1/work/pgpt-runs/PG379/media_range_port_driver.py run metadata f85525d010e5bf9af763cf584588921d0d0a1068`と同sourceの`post metadata`。input011/PG19000compile/PG19002static/正常APIjar等pinが必要。
