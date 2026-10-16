package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.api.maintenance.InspectorDbCredential;
import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.MaintenanceActivation;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxHostDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.channels.SeekableByteChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.sql.Connection;
import java.sql.DriverManager;
import java.time.Instant;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Optional;
import java.util.Properties;
import java.util.UUID;

/** SSC286/BUG1332. Read-only graph cost under real M/A/RODB, never a Root or permit. */
public final class RootOriginalReadProfile {
  private RootOriginalReadProfile() {}
  private static final Map<String, long[]> TIMES = new LinkedHashMap<>();
  private static final BufferedReader INPUT =
      new BufferedReader(new InputStreamReader(System.in, StandardCharsets.US_ASCII));
  private static final MaintenanceActivation ORIGINAL = new MaintenanceActivation(
      new BatchRun(UUID.fromString("dc0cb75f-1dbd-4b64-bb1c-b4d91e592c4f"),
          Instant.parse("2026-10-16T05:44:47.267413Z")),
      UUID.fromString("d9d58371-bf80-49f6-bad9-3d1e0916fb04"));

  private static void require(boolean value) throws IOException {
    if (!value) throw new IOException("readonly original profile refused");
  }

  private static void record(String name, long began) {
    var v = TIMES.computeIfAbsent(name, ignored -> new long[2]);
    v[0]++; v[1] += System.nanoTime() - began;
  }

  private static void frame(String value) throws IOException {
    System.out.println(value); System.out.flush();
    require("CONTINUE".equals(INPUT.readLine()));
  }

  @FunctionalInterface private interface Work<T> { T run() throws Exception; }
  private static <T> T checked(Work<T> work) throws IOException {
    try { return work.run(); }
    catch (Exception failure) { throw new IOException("readonly original profile failed"); }
  }

  private static Connection database() throws Exception {
    Path source = Path.of("/etc/schubert-nk/credentials/db-batch");
    String attrs = "unix:uid,gid,mode,nlink,size,dev,ino,ctime,lastModifiedTime";
    var before = Files.readAttributes(source, attrs, LinkOption.NOFOLLOW_LINKS);
    require(Integer.valueOf(0).equals(before.get("uid")) && Integer.valueOf(0).equals(before.get("gid"))
        && Integer.valueOf(0100600).equals(before.get("mode")) && Integer.valueOf(1).equals(before.get("nlink"))
        && (Long) before.get("size") > 0 && (Long) before.get("size") <= 65536);
    try (var held = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), source.getParent())) {
      held.atExistingEntryHandle("db-batch", path -> {
        require(Files.readAttributes(path, attrs).equals(before));
        require(LinuxInodeSecurity.create().accessAcl(path, 44).length == 0);
        return Boolean.TRUE;
      });
    }
    byte[] bytes = Files.readAllBytes(source);
    require(before.equals(Files.readAttributes(source, attrs, LinkOption.NOFOLLOW_LINKS)));
    try (var password = InspectorDbCredential.consume(bytes)) {
      char[] chars = password.copyPassword(); var props = new Properties();
      try {
        props.setProperty("user", "schubert_batch"); props.setProperty("password", new String(chars));
        props.setProperty("connectTimeout", "3"); props.setProperty("socketTimeout", "5");
        return DriverManager.getConnection("jdbc:postgresql://127.0.0.1:5432/schubert_nk", props);
      } finally { Arrays.fill(chars, '\0'); props.clear(); Arrays.fill(bytes, (byte) 0); }
    }
  }

  private static void heartbeat(Connection database, int expected) throws Exception {
    require(!database.isClosed() && database.isReadOnly() && !database.getAutoCommit());
    try (var s = database.createStatement(); var r = s.executeQuery(
        "select pg_backend_pid(),current_user,session_user,current_database(),"
        + "current_setting('transaction_read_only'),current_setting('application_name'),"
        + "exists(select 1 from pg_locks where pid=pg_backend_pid() and locktype='advisory'"
        + " and classid=0 and objid=71419602 and objsubid=1 and mode='ExclusiveLock' and granted)")) {
      require(r.next() && r.getInt(1) == expected && !r.wasNull()
          && "schubert_batch".equals(r.getString(2)) && "schubert_batch".equals(r.getString(3))
          && "schubert_nk".equals(r.getString(4)) && "on".equals(r.getString(5))
          && "PG286-original-profile".equals(r.getString(6)) && r.getBoolean(7) && !r.wasNull() && !r.next());
    }
  }

  private static MaintenanceRunFiles.Io measured() {
    var actual = new MaintenanceRunFiles.NioIo();
    return new MaintenanceRunFiles.Io() {
      public Map<String, Object> attributes(Path p) throws IOException {
        long at = System.nanoTime(); try { return actual.attributes(p); }
        finally { record("attributes", at); }
      }
      public String filesystem(Path p) throws IOException {
        long at = System.nanoTime(); try { return actual.filesystem(p); }
        finally { record("filesystem", at); }
      }
      public SeekableByteChannel open(Path p) throws IOException {
        long at = System.nanoTime(); try { return actual.open(p); }
        finally { record("open", at); }
      }
      public DirectoryStream<Path> openNames(Path p) throws IOException {
        long at = System.nanoTime(); try { return actual.openNames(p); }
        finally { record("names", at); }
      }
      public InspectorEnvironmentPublisher.Writer openWriter(Path p) throws IOException {
        throw new IOException("read-only profile never writes originals");
      }
    };
  }

  private static InodeSecurityCalls measuredSecurity() {
    var actual = LinuxInodeSecurity.create();
    return new InodeSecurityCalls() {
      public byte[] accessAcl(Path p, int bound) throws dev.codex.schubert.nk.storage.StorageIoException {
        long at = System.nanoTime(); try { return actual.accessAcl(p, bound); }
        finally { record("acl", at); }
      }
      public boolean readOnlyFilesystem(Path p) throws dev.codex.schubert.nk.storage.StorageIoException {
        long at = System.nanoTime(); try { return actual.readOnlyFilesystem(p); }
        finally { record("readonly", at); }
      }
      public long effectiveUid() { return actual.effectiveUid(); }
    };
  }

  public static void main(String[] args) throws Exception {
    require(args.length == 0 && LinuxInodeSecurity.create().effectiveUid() == 0);
    require(MaintenanceFileLock.create().tryExclusive(() -> checked(() ->
        StartupAdmissionFile.create().tryExclusive(admission -> checked(() -> {
          try (var db = database()) {
            db.setReadOnly(true); db.setAutoCommit(false); int backend;
            try (var s = db.createStatement(); var r = s.executeQuery(
                "select pg_backend_pid(),set_config('application_name','PG286-original-profile',false),pg_try_advisory_lock(71419602)")) {
              require(r.next()); backend = r.getInt(1); require(!r.wasNull() && r.getBoolean(3) && !r.wasNull() && !r.next());
            }
            heartbeat(db, backend); frame("ORIGINAL_PROFILE_READY " + backend);
            var files = new MaintenanceRunFiles(Path.of("/var"), LinuxDirectoryCalls.create(),
                measuredSecurity(), measured(), UUID::randomUUID,
                () -> MessageDigest.getInstance("SHA-256"), Optional.of(LinuxHostDirectoryCalls.create()));
            files.execute(session -> {
              long at = System.nanoTime(); session.verifyRetained(); record("retained", at);
              at = System.nanoTime(); var first = session.observeStartup(ORIGINAL); record("graph-first", at);
              require(first.activation().equals(ORIGINAL) && first.completed().isPresent()
                  && first.completed().orElseThrow().outcome().exitCode() == 10);
              at = System.nanoTime(); require(first.equals(session.observeStartup(ORIGINAL))); record("graph-second", at);
              at = System.nanoTime(); session.verifyRetained(); record("retained", at);
              return Boolean.TRUE;
            });
            heartbeat(db, backend); frame("ORIGINAL_PROFILE_MEASURED");
            db.rollback();
          }
          return Boolean.TRUE;
        })).orElseThrow())).orElseThrow());
    frame("ORIGINAL_PROFILE_CLOSED");
    for (var e : TIMES.entrySet()) System.out.println("READONLY_PROFILE1 phase=" + e.getKey()
        + " count=" + e.getValue()[0] + " nanos=" + e.getValue()[1]);
    System.out.println("ORIGINAL_PROFILE_NORMAL_RETURN");
  }
}
