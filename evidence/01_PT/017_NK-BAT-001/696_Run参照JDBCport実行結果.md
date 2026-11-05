# Run参照 JDBC port実行結果

{
  "atJST": "2026-11-05T15:40:36.228316+09:00",
  "source": "5920b9bc2483194f3ad1474fb9e933a97fa44587",
  "productionCoreMain": "b09393b0e746b55fd480176d57996d65bd76a95d",
  "run": "PG18984",
  "actualExit": 0,
  "tests": 8,
  "testClasses": 1,
  "failures": 0,
  "errors": 0,
  "skipped": 0,
  "aborted": 0,
  "coverage": {
    "dev/codex/schubert/nk/batch/repository/RunReferenceRepository": {
      "INSTRUCTION": {
        "covered": 206,
        "missed": 0
      },
      "BRANCH": {
        "covered": 24,
        "missed": 0
      },
      "LINE": {
        "covered": 52,
        "missed": 0
      },
      "COMPLEXITY": {
        "covered": 16,
        "missed": 0
      },
      "METHOD": {
        "covered": 4,
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
    "dev/codex/schubert/nk/api/error/TemporaryInfrastructureException": 0,
    "dev/codex/schubert/nk/api/idempotency/FingerprintKeyRing": 0,
    "dev/codex/schubert/nk/web/bootstrap/WebStartupException": 0
  },
  "manifest": "evidence/01_PT/017_NK-BAT-001/evidence/PG18984-run-reference-port-eight-v1/manifest.json",
  "manifestSha256": "c8f14f61046268cf8fa6d70076eb1c8473cafa28c97a88fe01af76f82eb098b9",
  "environmentSha256": "fb92317000bb8d1fba2de731b91cc12be737cd92f2fb2aac131283dd358f2126",
  "baseline80SamePathHash": true,
  "PG": "Main unchanged; SQL/5stimeout/UTCbind/4booleans, nullableacquisitions/columns/row0-2/16tuples, borrowedTXflags, allproviderSQL-RTE-Error/legacycloseprecedence, ownworkerIRQpreserved thenownedclear, separateparentconcurrency",
  "oracle": "literalSQL/UUID/UTC/booleanbits andSSC063handfailuretable, no productionexpectedgeneration",
  "static": "PG18982raw30 exactper-findingNA788, applicable0/CS0/parser0, fullMain6buildNullAway/SBPG18642/18648 sameb093inputs/jars reused",
  "originalFailure": "initialstatic18978raw31/entrylabel1applicable preregBUG2287/YKT2032 then5identicalliteralsconst. Initialcompile/static/producer preserved; firstproduct8 allsuccess",
  "oldExecUnion": false,
  "realDbRootVmFileLockNativeAuthorityOrCredential": false,
  "limitations": "not actualsingleparentlock/DBfunction/isolation/durability/file-removaleligibility/fatalgraphcrossscope/parentWBS/V/451",
  "formalUpdated": false,
  "newAccepted": 0,
  "effortRate": null,
  "originalPartial80": {
    "wholeTechnical": 9,
    "notYetWholeBound": 71,
    "globalRegistryChanged": false
  },
  "cost": {
    "startEstimatePp": {
      "low": 1,
      "base": 3,
      "high": 7
    },
    "capPp": 10,
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
      "observedByJST": "2026-11-05 15:37:09 JST",
      "provenance": "fresh get_usage_limits direct structured response",
      "previousObservationSha256": "2c10e0b13f8cf41b98ede17682a64453f2a5e6f658c193aa91fd13d13892a872"
    },
    "afterPostTimeGuard": true,
    "actualAllocatedPp": null,
    "N": null,
    "T": null,
    "reportedSharedPp": 0,
    "zeroNotFree": true
  }
}

695のRUNPORT001～008は全selectedTestMethods/元XMLで一意対応。時刻/argv/OS終了値はstage exit、元XMLhashから環境をwhitelist抽出。再現（成功確認だけの反復なし）：`env PYTHONPATH=tools/quality python3 -B /home/mini/codex/project1/work/pgpt-runs/PG379/media_range_port_driver.py run run_reference 5920b9bc2483194f3ad1474fb9e933a97fa44587`と同sourceの`post run_reference`。input695/PG18980compile/PG18982static/正常Batchjar等pinが必要。
