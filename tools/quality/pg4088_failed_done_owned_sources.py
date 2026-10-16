"""SSC287 fixed operational-source builder. Import/build never starts or stops a service."""
import ast
import hashlib
from pathlib import Path
import pg4084_recovery_inspection as inspection
import pg4086_failed_done_recovery_contract as contract

TOOLS = 'pg4088-failed-done-owned-tools-v1'
INSPECT = 'pg4090-failed-done-owned-inspect-v1'
RECOVER = 'pg4092-failed-done-owned-recover-v1'


def java():
    raw = inspection.java(); raw = raw[:raw.index('  public static void main')]
    raw = raw.replace('RootRecoveryInspect', 'RootFailedDoneRecovery')
    a = raw.index('  private static void frame('); b = raw.index('  @FunctionalInterface', a)
    raw = raw[:a] + FRAME + raw[b:]
    return raw + JAVA_END


FRAME = r'''
  private static void frame(String message, Work<Boolean> pulse) throws Exception {
    require(message != null && pulse != null && !Thread.currentThread().isInterrupted());
    System.out.println(message); System.out.flush();
    long start = System.nanoTime(), last = start;
    var bytes = new java.io.ByteArrayOutputStream();
    while (System.nanoTime() - start < java.util.concurrent.TimeUnit.SECONDS.toNanos(180)) {
      require(!Thread.currentThread().isInterrupted());
      long now = System.nanoTime();
      if (now - last >= java.util.concurrent.TimeUnit.SECONDS.toNanos(1)) {
        require(Boolean.TRUE.equals(pulse.run())); last = now;
      }
      require(!Thread.currentThread().isInterrupted());
      while (System.in.available() > 0) {
        int value = System.in.read(); require(value >= 0 && bytes.size() < 32); bytes.write(value);
        if (value == 10) {
          require(Arrays.equals(bytes.toByteArray(), "CONTINUE\n".getBytes(StandardCharsets.US_ASCII)));
          require(!Thread.currentThread().isInterrupted());
          return;
        }
      }
      require(!Thread.currentThread().isInterrupted());
      java.util.concurrent.locks.LockSupport.parkNanos(java.util.concurrent.TimeUnit.MILLISECONDS.toNanos(5));
    }
    throw new IOException("recovery framing deadline");
  }

'''


JAVA_END = r'''
  private static void revokeRuntime() throws IOException {
    try (var directory = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),
        Path.of("/run/schubert-nk/startup"))) {
      var files = new StartupPermitFiles(directory, LinuxInodeSecurity.create());
      var epoch = files.current(); var permit = files.readIssued();
      require(epoch.state() == StartupPermitRecords.State.ISSUED
          && epoch.boot().toString().equals("79a3260a-e16d-42bf-942a-b914ed144c28")
          && epoch.activation().equals(ORIGINAL)
          && permit.releaseDigest().equals("0a409301e552d8019440edcbf096ad9b20c15b35c0ee6472cd9c4cef65bd8dab"));
      var invalid = new StartupPermitRecords.Epoch(StartupPermitRecords.State.INVALID,
          epoch.boot(), epoch.epoch(), epoch.activation(), Optional.empty());
      require(invalid.equals(files.revoke(invalid, permit)) && invalid.equals(files.current()));
      var historical = files.readRevoked(invalid);
      require(historical.formerIssued().equals(epoch) && historical.permit().equals(permit));
      // No intent exists in this fixed cohort. No owner/launch/permit file is retired or recreated.
      StartupLaunchFiles.requireNoServiceResidue(directory, LinuxInodeSecurity.create());
    }
  }

  private static void retain() {
    System.err.println("RECOVERY_UNKNOWN newOwnershipRetained=true oldParent143StillFailed=true diagnosticsRedacted=true");
    for (;;) {
      java.util.concurrent.locks.LockSupport.parkNanos(java.util.concurrent.TimeUnit.SECONDS.toNanos(1));
      Thread.interrupted();
    }
  }

  public static void main(String[] args) throws Exception {
    require(args != null && args.length == 1 && (args[0].equals("inspect") || args[0].equals("recover"))
        && LinuxInodeSecurity.create().effectiveUid() == 0);
    boolean recovery = args[0].equals("recover");
    try {
    require(MaintenanceFileLock.create().tryExclusive(() -> checked(() -> {
      try {
        return StartupAdmissionFile.create().tryExclusive(admission -> checked(() -> {
          try {
            var db = database();
            db.setReadOnly(true); db.setAutoCommit(false); int backend;
            try (var s = db.createStatement(); var r = s.executeQuery(
                "select pg_backend_pid(),set_config('application_name','PG286-original-profile',false),pg_try_advisory_lock(71419602)")) {
              require(r.next()); backend = r.getInt(1); require(!r.wasNull() && r.getBoolean(3) && !r.wasNull() && !r.next());
            }
            Work<Boolean> pulse = () -> { heartbeat(db, backend); return Boolean.TRUE; };
            heartbeat(db, backend); frame("RECOVERY_READY " + backend, pulse);
            inspectRuntime();
            if (recovery) {
              for (String unit : java.util.List.of("caddy.service", "schubert-nk-web.service",
                  "schubert-nk-api.service", "schubert-nk-expiry-cleanup.service", "artemis.service",
                  "schubert-nk-cleanup.service")) {
                frame("RECOVERY_STOP " + unit, pulse); heartbeat(db, backend);
              }
              inspectRuntime(); frame("RECOVERY_TERMINAL", pulse); heartbeat(db, backend);
              revokeRuntime(); frame("RECOVERY_REVOKED", pulse); heartbeat(db, backend);
            } else frame("RECOVERY_INSPECTED", pulse);
            db.rollback(); db.close(); require(db.isClosed());
            return Boolean.TRUE;
          } catch (Exception | Error failure) { retain(); throw failure; }
        })).orElseThrow();
      } catch (Exception | Error failure) { retain(); throw failure; }
    })).orElseThrow());
    } catch (Exception | Error failure) { retain(); throw failure; }
    frame("RECOVERY_CLOSED", () -> Boolean.TRUE);
    System.out.println("RECOVERY_NORMAL_RETURN oldParentNormal=false");
  }
}
'''


def files():
    values = contract.shared_sources()
    source = (Path(__file__).resolve().parent / 'pg4086_failed_done_recovery_contract.py').read_text()
    selected = []
    for n in ast.parse(source).body:
        if isinstance(n, (ast.Import, ast.ImportFrom)):
            if isinstance(n, ast.Import) and all(a.name in {'re', 'uuid'} for a in n.names): selected.append(n)
        elif isinstance(n, ast.FunctionDef) and n.name in {'require', 'invalid_epoch'}: selected.append(n)
        elif isinstance(n, ast.ClassDef) and n.name == 'Plan': selected.append(n)
        elif isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'ORDER' for t in n.targets): selected.append(n)
    values['recovery_plan.py'] = ast.unparse(ast.Module(body=selected, type_ignores=[])) + '\n'
    values['RootFailedDoneRecovery.java'] = java()
    for name, raw in values.items():
        if name.endswith('.py'): compile(raw, '<fixed operational helper ' + name + '>', 'exec')
    return values


def hashes():
    return {name: hashlib.sha256(raw.encode()).hexdigest() for name, raw in files().items()}
