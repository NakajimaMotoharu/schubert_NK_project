"""New API monitor contexts; metadata only, no product execution."""
import static_context_reader_v1 as reader

PLAN = {
  "out": "PG14066-api-dispatch-observation-monitor-v1",
  "record": "evidence/01_PT/018_NK-OPS-001/2567_API_dispatch・observation同期十二_静的仕様.md",
  "rule": "AvoidSynchronizedStatement",
  "targets": {
    "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/inbound/ApiMessagingRuntime.java": {
      "sha256": "b67514d342a8f3be8891bb30c003731a98a6dc484814f873dcdb8a85414f60ed",
      "owner": "WBS-P005-03",
      "ids": [
        "PMD-00191"
      ],
      "reason": "SS321/342の所有順を保つprivate closeLock。stoppingを先に公開しcloseGroupsを直列化、成功groupのみ記憶し全成功後だけclosed。全group逆順attemptとError順位はSource契約。実JMSclose/UNKNOWN外部保持・native block/期限は未実証、readyは全体証明でない。",
      "guards": [
        "private final Object closeLock = new Object();",
        "stopping.set(true);",
        "if (closed) return;",
        "closeGroups(groups, groupClosed);",
        "closed = true;",
        "for (int index = groups.size() - 1; index >= 0; index--)",
        "if (groupClosed[index]) continue;",
        "groups.get(index).close();",
        "groupClosed[index] = true;"
      ],
      "ordered": [],
      "prefixLines": None,
      "prefixSha256": None,
      "monitor": "closeLock"
    },
    "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/outbound/OwnedOutboxDispatcher.java": {
      "sha256": "8f2eb236d04f8fce43b4fdad94f6323bdf17c574d79e5a5b09e981abe9e1a30a",
      "owner": "WBS-P006-02",
      "ids": [
        "PMD-00315",
        "PMD-00316",
        "PMD-00317",
        "PMD-00318",
        "PMD-00321",
        "PMD-00323",
        "PMD-00326"
      ],
      "reason": "SS324のcommit後wakeとdispatch所有をprivate lockで直列化。start/stopping/failed/signalledの可視性とwait/notifyを同monitorに置き、実dispatchとjoinはmonitor外。停止要求とthread実終端を混同しない。100msは内部wakeで承認業務backoffではない。無上限join/DB-JMS滞留・外stop budget/native連鎖は未受入のまま。",
      "guards": [
        "private final Object lock = new Object();",
        "if (started || stopping) throw new IllegalStateException",
        "if (!started || stopping || failed)",
        "return started && !stopping && !failed;",
        "if (!signalled) lock.wait(100);",
        "dispatcher.dispatch(owner, 32);",
        "failed = true;",
        "if (Thread.currentThread() == worker)",
        "while (worker.isAlive())",
        "if (interrupted) Thread.currentThread().interrupt();"
      ],
      "ordered": [
        [
          "stopping = true;",
          "while (worker.isAlive())"
        ]
      ],
      "prefixLines": None,
      "prefixSha256": None,
      "monitor": "lock"
    },
    "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/ApiOutboxObservationPump.java": {
      "sha256": "25eed3a03c68fd2f0bb7c68bf576239e238a2e2ecd4b4003ddc3d076348c2f41",
      "owner": "WBS-P018-09",
      "ids": [
        "PMD-00332"
      ],
      "reason": "SS351の欠測とSTANDARD/DEBUG、呼出側保持の既stop budgetを維持するprivate claim lock。cadence claimとmissing/activeを確定後にmonitor外でattempt取得/read。未解放resourceをunconfirmedへ固定し停止中は値を公開しない。callback clock/attempt/readの有界性と実DB cleanupは未実証。",
      "guards": [
        "private final Object lock = new Object();",
        "if (!detailed || stopping.get() || unconfirmed.get() || active.get()) return;",
        "now = nanos.getAsLong();",
        "if (previouslyClaimed && now - lastClaim < intervalNanos) return;",
        "source.missing();",
        "active.set(true);",
        "Objects.requireNonNull(attempts.get(), \"prepared observation attempt\")",
        "unconfirmed.set(true);",
        "return !active.get() && !unconfirmed.get();"
      ],
      "ordered": [
        [
          "active.set(true);",
          "Objects.requireNonNull(attempts.get(), \"prepared observation attempt\")"
        ]
      ],
      "prefixLines": None,
      "prefixSha256": None,
      "monitor": "lock"
    },
    "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/ApiOutboxObservationSource.java": {
      "sha256": "1d2c0e44fab847e256b794a04bdabd3bf770db3deb59afe37c8e3a80faaccc3d",
      "owner": "WBS-P018-09",
      "ids": [
        "PMD-00335",
        "PMD-00336"
      ],
      "reason": "SS351観測欠測は0値とせずprivate writerLock内でwriterを直列化。毎回新Entry identityを置きread/cleanup後CASだけで公開、missingが新identityを置けば旧readは再公開不可。borrowed Connectionとone-shot readを区別する。実SQL/cleanup/driverのmonitor滞留・全経路停止は未実証、getはimmutable値参照のみ。",
      "guards": [
        "private final Object writerLock = new Object();",
        "Entry pending = new Entry(Optional.empty());",
        "Optional<Snapshot> supplied = Optional.of(repository.read(connection, asOf));",
        "Optional<Snapshot> supplied = Optional.of(attempt.read());",
        "if (current.compareAndSet(pending, new Entry(supplied))) return supplied;",
        "current.set(new Entry(Optional.empty()));",
        "return current.get().observation;"
      ],
      "ordered": [],
      "prefixLines": None,
      "prefixSha256": None,
      "monitor": "writerLock"
    },
    "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/OwnedApiObservationWorker.java": {
      "sha256": "8bd8e156ff5038f7e5783865523913e2a0cf6188d674de05c9892ccecc6b0bbf",
      "owner": "WBS-P018-09",
      "ids": [
        "PMD-00372"
      ],
      "reason": "SS342/351のcaller-owned observation worker。private startLockでattempted/stoppingの一回claimを固定しstarterはmonitor外。startReturned finallyとstarting flagによりstart競合を呼出側既残budgetから待つ。stop unconfirmedを永久保持しborrowed pool解放成功へ変換しない。callback/fatal graph/実thread stop/Unitは未実証HOLD。",
      "guards": [
        "private final Object startLock = new Object();",
        "if (attempted || stopping.get())",
        "attempted = true;",
        "starting.set(true);",
        "starter.accept(worker);",
        "startReturned.countDown();",
        "Math.min(firstRemaining - elapsed, remainingNanos.getAsLong())",
        "if (!pump.isQuiescent()) throw new IOException(UNCONFIRMED);",
        "unconfirmedStop.set(true);"
      ],
      "ordered": [
        [
          "attempted = true;",
          "starter.accept(worker);"
        ]
      ],
      "prefixLines": None,
      "prefixSha256": None,
      "monitor": "startLock"
    }
  },
  "design": {
    "documents/300_SS/320_メッセージング/321_Artemis物理構成・JMS設定設計.md": "2fbf317dcc6d2048abb3c8ecdc9747e7b3d46cdba4753bec6bbc9e3ace5d5d1c",
    "documents/300_SS/320_メッセージング/324_Outbox・Inbox・冪等性・再送設計.md": "2bc99fd66ca1121a1ab4ae44e97aab96b52d4cf4c8145f6a425f89c7b07ce774",
    "documents/300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md": "3775cb1faf0b96572f4913d06682100da1861f1d364a66f4118b03e27abf4b82",
    "documents/300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md": "9da7c4e4f24740e031f37f984ec562d56e14ff098b1433af3ec55fe15bd195e6"
  }
}

if __name__ == '__main__':reader.run(PLAN)
