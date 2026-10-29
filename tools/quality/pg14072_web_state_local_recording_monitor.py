"""Six new Source contracts, no Java/native/credential or service execution."""
import static_context_reader_v1 as reader

PLAN = {
  "out": "PG14072-web-state-local-recording-monitor-v1",
  "record": "evidence/01_PT/018_NK-OPS-001/2569_Web状態・局所記録同期十_静的仕様.md",
  "rule": "AvoidSynchronizedStatement",
  "targets": {
    "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/ContextHash.java": {
      "sha256": "9b0714ec9dc88f3f15e11341d71d873250fee8436ebad03b3fb1079060392581",
      "owner": "WBS-P007-03",
      "ids": [
        "PMD-00393"
      ],
      "monitor": "stateLock",
      "reason": "SS314§6 raw ASCII SHA256を共有MessageDigestのprivate monitorで直列化。出力はlower hex、rawとdigest byte配列は各finallyでwipe。caller monitorへ依存せず、hash結果をlogしない。JCA実装の有界性/実認証結果/暗号vectorは本静的点検の資格でない。",
      "guards": [
        "private final Object stateLock = new Object();",
        "MessageDigest.getInstance(\"SHA-256\")",
        "context.wireValue().getBytes(StandardCharsets.US_ASCII)",
        "byte[] hashed = digest.digest(raw);",
        "return HexFormat.of().formatHex(hashed);",
        "Arrays.fill(hashed, (byte) 0);",
        "Arrays.fill(raw, (byte) 0);"
      ],
      "ordered": [],
      "prefixLines": None,
      "prefixSha256": None
    },
    "src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/monitoring/BatchMetricRecorder.java": {
      "sha256": "248563d0e9454cb496734c8d6c5b167c0ba3a7cc7fc9bcf6aca0e808c539a12d",
      "owner": "WBS-P018-09",
      "ids": [
        "PMD-02958"
      ],
      "monitor": "lock",
      "reason": "SS351のcaller-proven terminal metadataだけを借用registryへ記録。時刻µs/range検査後STANDARDは無記録、private lockでcounterとlastSuccessの単調最大を更新し欠測はNaN。metricはbatch成功やdedup authorityでない。registry callback/実batch/並行完了は未測定。",
      "guards": [
        "private final Object lock = new Object();",
        "if (!collectDetailed) return;",
        "endedAt.getNano() % NANOS_PER_MICROSECOND != 0",
        "if (status == Status.SUCCESS)",
        "if (previous.isEmpty() || endedAt.isAfter(previous.orElseThrow()))",
        "state.set(Optional.of(endedAt));",
        ".orElse(Double.NaN);"
      ],
      "ordered": [],
      "prefixLines": None,
      "prefixSha256": None
    },
    "src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/FixedNativeCoverageCheckpoint.java": {
      "sha256": "95d70220aaa00265151d92ec1c4d4e5e7e220ed4508668461ce0b497b988e86d",
      "owner": "WBS-P018-08",
      "ids": [
        "PMD-06152"
      ],
      "monitor": "lock",
      "reason": "SS343/451隔離PTのagent export一回claim。private lock下でagent/I/O前にpoint消費、closingはterminal成功後だけ。version/sessionを前後検査、reset無しsnapshotとclone export、未知/部分captureを再試行しない。実agent/native/FS exportは起動0、headerだけでCRCや全coverage資格を認定しない。",
      "guards": [
        "private final Object lock = new Object();",
        "if (!attempted.add(point)) throw unavailable();",
        "if (point == Point.CLOSING) require(terminalCompleted);",
        "byte[] value = agent.executionDataWithoutReset();",
        "export.write(profile.invocation() + suffix, value.clone());",
        "if (point == Point.TERMINAL) terminalCompleted = true;",
        "new Object[] {false}"
      ],
      "ordered": [
        [
          "if (!attempted.add(point)) throw unavailable();",
          "byte[] value = agent.executionDataWithoutReset();",
          "export.write(profile.invocation() + suffix, value.clone());",
          "if (point == Point.TERMINAL) terminalCompleted = true;"
        ]
      ],
      "prefixLines": None,
      "prefixSha256": None
    },
    "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebHttpServer.java": {
      "sha256": "b1e458ef9a9a246f8bb70866dbf671a005bbb569b9c4e27c20b525c20b3180a5",
      "owner": "WBS-P018-06",
      "ids": [
        "PMD-07211",
        "PMD-07217",
        "PMD-07218",
        "PMD-07219"
      ],
      "monitor": "lifecycleLock",
      "reason": "SS313/342 private lifecycleLockでstarted/closedとvendor stop/destroy段階を直列化。ownerをvendor mutation前に捕捉しstartedはcontext STARTED後だけ。port/mappingsはstartedかつnotclosedのみ、stop成功後だけstopped、destroy成功後だけdestroyed。vendor/mapper callbackはlock内となり有界性と並行停止実証は未取得、native ownerの外budgetへ合算しない。",
      "guards": [
        "private final Object lifecycleLock = new Object();",
        "if (owner != None) owner.accept(result);",
        "if (context.getState() != LifecycleState.STARTED)",
        "result.started = true;",
        "if (closed || !started) throw new IllegalStateException",
        "if (destroyed) return;",
        "closed = true;",
        "tomcat.stop();",
        "stopped = true;",
        "tomcat.destroy();",
        "destroyed = true;"
      ],
      "ordered": [
        [
          "tomcat.stop();",
          "stopped = true;"
        ]
      ],
      "prefixLines": None,
      "prefixSha256": None
    },
    "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebLogApplicationRuntime.java": {
      "sha256": "24759417295528fcda7b59a4c3055c2310ed406b6a507ebdb3af581cc8558498",
      "owner": "WBS-P006-04",
      "ids": [
        "PMD-07221"
      ],
      "monitor": "stopLock",
      "reason": "SS321/324/342借用依存を残すprivate stopLock。http→replay→repliesの順、成功phaseだけadvance、途中UNKNOWNでは下流解放せずretryable owner保持、closedは全終端後。startup cleanup UNKNOWNの原無限保持を動的試験しない。graph classifier/実drain/実stop/外期限は未受入HOLD、ローカルreadyを全体readyへ昇格しない。",
      "guards": [
        "private final Object stopLock = new Object();",
        "if (closed.get()) return;",
        "stopping.set(true);",
        "var resources = new AutoCloseable[] {http, replay, replies};",
        "resources[stoppedResources].close();",
        "stoppedResources++;",
        "closed.set(true);",
        "SessionStoreException.preserveFatal(closing);"
      ],
      "ordered": [
        [
          "resources[stoppedResources].close();",
          "stoppedResources++;",
          "closed.set(true);"
        ]
      ],
      "prefixLines": None,
      "prefixSha256": None
    },
    "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebNativeRuntime.java": {
      "sha256": "c9701244fed7a903c0858a5b8ef4bd78a3ddd499b76bbb9358a5f7181c4bec45",
      "owner": "WBS-P018-06",
      "ids": [
        "PMD-07254",
        "PMD-07261"
      ],
      "monitor": "ownerLock",
      "reason": "SS342/343一つのnative partial ownerをprivate ownerLockでstart/close直列化。startAttempted先行、全業務map/management成立後だけready release+admit。closeは最初のstop.beginを保持してadmission拒否、drain/http/retry/replay/replies/management/metrics/assets/transfer/codecs/brokerのphase。lock獲得待ち自体やvendor/native/DB/JMS/鍵の終了時間はSource reviewだけで実証しない。旧native資格移植0。",
      "guards": [
        "private final Object ownerLock = new Object();",
        "if (startAttempted || stopping.get())",
        "startAttempted = true;",
        "requireMappings(Objects.requireNonNull(http).mappedPaths());",
        "retainedReady.release();",
        "admission.admit();",
        "if (stopping.compareAndSet(false, true)) stop.begin();",
        "admission.refuse();",
        "WebRuntimeStop.Step[] phases = {",
        "stop.close(phases);"
      ],
      "ordered": [
        [
          "startAttempted = true;",
          "requireMappings(Objects.requireNonNull(http).mappedPaths());",
          "retainedReady.release();",
          "admission.admit();"
        ]
      ],
      "prefixLines": None,
      "prefixSha256": None
    }
  },
  "design": {
    "documents/300_SS/320_メッセージング/321_Artemis物理構成・JMS設定設計.md": "2fbf317dcc6d2048abb3c8ecdc9747e7b3d46cdba4753bec6bbc9e3ace5d5d1c",
    "documents/300_SS/320_メッセージング/324_Outbox・Inbox・冪等性・再送設計.md": "2bc99fd66ca1121a1ab4ae44e97aab96b52d4cf4c8145f6a425f89c7b07ce774",
    "documents/300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md": "3775cb1faf0b96572f4913d06682100da1861f1d364a66f4118b03e27abf4b82",
    "documents/300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md": "9da7c4e4f24740e031f37f984ec562d56e14ff098b1433af3ec55fe15bd195e6",
    "documents/300_SS/310_アプリケーション/314_認証・認可・session・CSRF実装設計.md": "ab7a1907d0861ca1b6d4181d674f98a73c13f8a4b897b86f655b5a30ce202a7b",
    "documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md": "d8be70ce4c170df7939f7803723bb021c99ba40a72819f9b5d861731425332b2"
  }
}

if __name__ == '__main__':reader.run(PLAN)
