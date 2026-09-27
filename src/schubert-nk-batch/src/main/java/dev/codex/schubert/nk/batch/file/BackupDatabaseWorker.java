package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.require;

import dev.codex.schubert.nk.api.file.InspectorCredentialLoader;
import dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.Metadata;
import dev.codex.schubert.nk.batch.platform.*;
import dev.codex.schubert.nk.bootstrap.*;
import dev.codex.schubert.nk.storage.*;
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;
import edu.umd.cs.findbugs.annotations.SuppressMatchType;
import java.io.IOException;
import java.nio.file.Path;
import java.util.*;
import org.jspecify.annotations.NullMarked;

/**
 * Fixed dedicated database worker only. NK-OPS-001/BAK/BKO/UI251/SS3416.1/343/SSC092/BWORK. Parent
 * owns M/A, authoritative run/step begin, namespace/release/role readiness, total30min and fresh
 * full Unit termination before any follow-up. Worker never updates DB step/manifest/retention.
 */
@NullMarked
public final class BackupDatabaseWorker {
  interface Ports {
    FixedServiceIdentity.Value identity() throws IOException;

    ChildStartupContext.Observed self() throws IOException;

    InspectorUnitSnapshot unit();

    String invocation();

    OwnedTransferDirectory credentials() throws IOException;

    OwnedTransferDirectory runtime() throws IOException;

    OwnedTransferDirectory backup() throws IOException;

    byte[] request(OwnedTransferDirectory credentials) throws IOException;

    byte[] pgpass(OwnedTransferDirectory credentials) throws IOException;

    void dump(Path output, Path pgpass, long uid) throws IOException;

    InspectorEnvironmentPublisher.Io io();

    InodeSecurityCalls security();
  }

  private final Ports ports;

  public BackupDatabaseWorker() {
    this(new NativePorts());
  }

  BackupDatabaseWorker(Ports ports) {
    this.ports = Objects.requireNonNull(ports, "fixed worker ports");
  }

  public static void main(String[] arguments) throws IOException {
    Objects.requireNonNull(arguments, "arguments");
    if (arguments.length != 0) throw new IOException("backup worker arguments refused");
    Thread.currentThread().setUncaughtExceptionHandler(BackupDatabaseWorker::fatal);
    new BackupDatabaseWorker().execute();
  }

  static void fatal(Thread thread, Throwable failure) {
    System.err.println("backup worker failed");
  }

  public void execute() throws IOException {
    var fixed = Objects.requireNonNull(ports.identity(), "fixed backup identity");
    var before = Objects.requireNonNull(ports.self(), "worker kernel identity");
    admit(fixed, before);
    var credentials = Objects.requireNonNull(ports.credentials(), "credential owner");
    ResourceScope.use(
        credentials::close,
        () -> {
          var request = BackupWorkerRequest.consume(ports.request(credentials));
          var runtime = Objects.requireNonNull(ports.runtime(), "runtime owner");
          return ResourceScope.use(
              runtime::close,
              () -> {
                Metadata ram = directory(runtime, fixed, true);
                var backup = Objects.requireNonNull(ports.backup(), "backup owner");
                return ResourceScope.use(
                    backup::close,
                    () -> {
                      Metadata parent = directory(backup, fixed, false);
                      require(parent.device() != ram.device() || parent.inode() != ram.inode());
                      String name = request.directoryName() + ".part";
                      var child = backup.createPrivateChild(name);
                      return ResourceScope.use(
                          child::close,
                          () -> {
                            Metadata original = directory(child, fixed, false);
                            require(original.device() == parent.device());
                            UUID file = UUID.randomUUID();
                            child.createPrivatePart(
                                file,
                                p -> {
                                  require(file(p, fixed).size() == 0);
                                  return true;
                                });
                            child.publishAs(file, "schubert_nk.dump");
                            child.atExistingEntryHandle(
                                "schubert_nk.dump",
                                output -> {
                                  Metadata empty = file(output, fixed);
                                  require(empty.device() == original.device() && empty.size() == 0);
                                  // BUG274: establish invariant/eraser before acquiring any owned
                                  // secret bytes.
                                  var copy =
                                      new BackupDatabaseCopy(
                                          runtime,
                                          ports.security(),
                                          fixed.uid(),
                                          fixed.gid(),
                                          ports.io());
                                  byte[] raw =
                                      Objects.requireNonNull(
                                          ports.pgpass(credentials), "owned pgpass");
                                  try {
                                    copy.dump(
                                        raw,
                                        UUID.randomUUID(),
                                        p -> ports.dump(output, p, fixed.uid()));
                                  } finally {
                                    Arrays.fill(raw, (byte) 0);
                                  }
                                  Metadata completed = file(output, fixed);
                                  require(
                                      completed.device() == empty.device()
                                          && completed.inode() == empty.inode()
                                          && completed.size() > 0);
                                  require(
                                      completed.equals(
                                          child.atExistingEntryHandle(
                                              "schubert_nk.dump", p -> file(p, fixed))));
                                  return true;
                                });
                            require(identity(original, directory(child, fixed, false)));
                            require(identity(parent, directory(backup, fixed, false)));
                            require(identity(ram, directory(runtime, fixed, true)));
                            require(fixed.equals(ports.identity()) && before.equals(ports.self()));
                            admit(fixed, before);
                            return true;
                          });
                    });
              });
        });
  }

  private void admit(FixedServiceIdentity.Value fixed, ChildStartupContext.Observed own)
      throws IOException {
    require(!Thread.currentThread().isInterrupted());
    require(
        own.uid() == fixed.uid()
            && own.gid() == fixed.gid()
            && own.groups().equals(fixed.groups()));
    require(own.zeroCapabilities() && own.noNewPrivileges());
    require(own.cgroup().equals("0::/system.slice/schubert-nk-backup.service\n"));
    require(
        Objects.requireNonNull(ports.unit(), "worker Unit").running(own.pid(), ports.invocation()));
  }

  private Metadata directory(
      OwnedTransferDirectory root, FixedServiceIdentity.Value fixed, boolean runtime)
      throws StorageIoException {
    return root.atDirectory(
        p -> {
          Metadata result = metadata(p, fixed, true);
          if (runtime) require("tmpfs".equals(ports.io().filesystem(p)));
          return result;
        });
  }

  private Metadata file(Path p, FixedServiceIdentity.Value fixed) throws IOException {
    return metadata(p, fixed, false);
  }

  private Metadata metadata(Path p, FixedServiceIdentity.Value fixed, boolean directory)
      throws IOException {
    Metadata m = EnvironmentInodePolicy.metadata(ports.io().attributes(p));
    require(
        m.mode() == (directory ? 040700 : 0100600)
            && m.uid() == fixed.uid()
            && m.gid() == fixed.gid());
    require(m.size() >= 0);
    if (directory) require(m.links() >= 2);
    else require(m.links() == 1);
    byte[] acl = ports.security().accessAcl(p, 44);
    require(acl != null && acl.length == 0);
    require(!ports.security().readOnlyFilesystem(p));
    return m;
  }

  private static boolean identity(Metadata before, Metadata after) {
    return before.device() == after.device() && before.inode() == after.inode();
  }

  static final class NativePorts implements Ports {
    private final InodeSecurityCalls security = LinuxInodeSecurity.create();
    private final DirectoryCalls calls = LinuxDirectoryCalls.create();
    private final InspectorEnvironmentPublisher.Io io = new InspectorEnvironmentPublisher.NioIo();
    private final FixedServiceIdentity nss = new FixedServiceIdentity();
    private final ChildStartupContext kernel = new ChildStartupContext();
    private final InspectorUnitProbe unit =
        InspectorUnitProbe.forTarget(InspectorUnitSnapshot.Target.BACKUP);

    public FixedServiceIdentity.Value identity() throws IOException {
      return nss.resolveBackup();
    }

    public ChildStartupContext.Observed self() throws IOException {
      return kernel.capture();
    }

    public InspectorUnitSnapshot unit() {
      return unit.read();
    }

    public String invocation() {
      return System.getenv().getOrDefault("INVOCATION_ID", "");
    }

    @SuppressFBWarnings(
        value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
        matchType = SuppressMatchType.EXACT,
        justification =
            "SS343/SSC092 mandates the exact systemd credential namespace; not a portable caller-supplied path")
    public OwnedTransferDirectory credentials() throws IOException {
      Path source = ServiceCredentialLocation.read(System.getenv()).directory();
      require(source.equals(Path.of("/run/credentials/schubert-nk-backup.service")));
      return OwnedTransferDirectory.open(calls, source);
    }

    @SuppressFBWarnings(
        value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
        matchType = SuppressMatchType.EXACT,
        justification =
            "SS343/SSC092 mandates the dedicated fixed private tmpfs root; no arbitrary root")
    public OwnedTransferDirectory runtime() throws IOException {
      return OwnedTransferDirectory.open(calls, Path.of("/run/schubert-nk-backup"));
    }

    @SuppressFBWarnings(
        value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
        matchType = SuppressMatchType.EXACT,
        justification =
            "SS343/SSC092 mandates the fixed backup root; parent admission is still mandatory")
    public OwnedTransferDirectory backup() throws IOException {
      return OwnedTransferDirectory.open(calls, Path.of("/srv/schubert-nk/backup"));
    }

    public byte[] request(OwnedTransferDirectory root) throws IOException {
      return new InspectorCredentialLoader(root, security).readBackupRequest();
    }

    public byte[] pgpass(OwnedTransferDirectory root) throws IOException {
      return new InspectorCredentialLoader(root, security).readBackupPgpass();
    }

    public void dump(Path out, Path pass, long uid) throws IOException {
      new BackupArchiveProcess(security).dump(out, pass, uid);
    }

    public InspectorEnvironmentPublisher.Io io() {
      return io;
    }

    public InodeSecurityCalls security() {
      return security;
    }
  }
}
