# Scenario Snapshot形状単体結果

{
  "atJST": "2026-11-05T15:18:25.723500+09:00",
  "source": "0420061453488a4dd642c1208dae3eaec5f17eac",
  "productionCoreMain": "b09393b0e746b55fd480176d57996d65bd76a95d",
  "run": "PG18964",
  "actualExit": 0,
  "tests": 6,
  "testClasses": 2,
  "failures": 0,
  "errors": 0,
  "skipped": 0,
  "aborted": 0,
  "coverage": {
    "dev/codex/schubert/nk/api/persistence/ScenarioDetailSnapshot": {
      "INSTRUCTION": {
        "covered": 81,
        "missed": 0
      },
      "BRANCH": {
        "covered": 6,
        "missed": 0
      },
      "LINE": {
        "covered": 18,
        "missed": 0
      },
      "COMPLEXITY": {
        "covered": 5,
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
    "dev/codex/schubert/nk/api/error/TemporaryInfrastructureException": 0,
    "dev/codex/schubert/nk/api/idempotency/FingerprintKeyRing": 0,
    "dev/codex/schubert/nk/web/bootstrap/WebStartupException": 0,
    "dev/codex/schubert/nk/api/idempotency/ResponseSnapshotCodec": 0
  },
  "manifest": "evidence/01_PT/008_NK-SCN-001/evidence/PG18964-scenario-snapshot-shape-six-v1/manifest.json",
  "manifestSha256": "29fbd0b49195a11819f1c8fac351457be410b89860b1f59f7c6a401c2f0e7cd9",
  "environmentSha256": "66cd678a4401b7e1d8675884d4bf74bfec91d62498c46b432e668b2ffde09201",
  "baseline80SamePathHash": true,
  "PG": "Main unchanged; INLINE/max10000 shape reviewed, FILE/10001 bothreject beforedataescapes, nullmetadata-list-elements constructorinvariants, immutable0/1/10000/sequence/tail wirechecks",
  "oracle": "independentliteral shape/count/body/exception plusexistingBoundary10000/gap/tail4097 inputs, not production expectedgenerated",
  "static": "PG18958PMD0/CS0/parser0/wholefileapplicable0; Main6buildNullAway/SBPG18642/18648 sameb093 exactinputs/jar reused",
  "originalFailure": "PG18956 compile1 privateSha256Hexconstructor, staticguard1 NOTRUN. BUG2285/YKT2030 preregistered and publishedfactoryof used; correctfactory/recordconstructors checked. Originalcompile/producer preserved, oldBoundary unchanged",
  "oldExecUnion": false,
  "actualBackendFileDbRootVmNativeOrAuth": false,
  "limitations": "not realfile/filehash/publisher/owner/DB/parentWBS/V/451",
  "formalUpdated": false,
  "newAccepted": 0,
  "effortRate": null,
  "originalPartial80": {
    "wholeTechnical": 8,
    "notYetWholeBound": 72,
    "globalRegistryChanged": false
  },
  "cost": {
    "originalStartEstimatePp": {
      "low": 0.5,
      "base": 1.5,
      "high": 4
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
      "observedByJST": "2026-11-05 15:08:23 JST",
      "provenance": "fresh get_usage_limits direct structured response",
      "previousObservationSha256": "f75ad2a4c22cb6cc69d8a92f6e236f2f5b9ed35d598f5416c896566b7d0b8410"
    },
    "actualAllocatedPp": null,
    "N": null,
    "T": null
  }
}

007のSHAPE001～003と既SNAPSHOTMAX001～003はselectedTestMethods/元XMLで一意対応。実時刻/command/終了codeはstage exit。再現（成功確認だけの反復なし）：`env PYTHONPATH=tools/quality python3 -B /home/mini/codex/project1/work/pgpt-runs/PG379/media_range_port_driver.py run snapshot 0420061453488a4dd642c1208dae3eaec5f17eac`と同sourceの`post snapshot`。input007/PG18960compile/PG18958static/正常APIjar等pinが必要。

費用観測時点の追記訂正：785/3850/BUG2286。元784/3849の15:08:23は開始観測と同じでpost後終端ではない。fresh15:19:15（post後）used15/残85で正規共有差0を確認、専有費0とはしない。原見積/全製品6/coverage/source/run不変更。
