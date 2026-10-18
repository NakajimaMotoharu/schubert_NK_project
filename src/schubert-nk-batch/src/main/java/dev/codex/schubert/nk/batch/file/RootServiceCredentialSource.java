package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.require;

import dev.codex.schubert.nk.api.maintenance.InspectorDbCredential;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.bootstrap.FixedServiceIdentity;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.LinuxHostDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ResourceScope;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;
import edu.umd.cs.findbugs.annotations.SuppressMatchType;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.SeekableByteChannel;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/** Fixed Root service source only; no ordinary credential catalog extension. SSC137/PT297. */
@NullMarked
final class RootServiceCredentialSource {
  @FunctionalInterface
  interface Work<T> {
    T execute(InspectorDbCredential database, InspectorDbCredential ops) throws IOException;
  }

  private RootServiceCredentialSource() {}

  static <T> T execute(RootStartupContext context, RootStartupContext.Snapshot self, Work<T> work)
      throws IOException {
    Objects.requireNonNull(context);
    Objects.requireNonNull(self);
    Objects.requireNonNull(work);
    require(
        self.service() == RootStartupContext.Service.API
            || self.service() == RootStartupContext.Service.WEB);
    context.recheck(self);
    var service =
        self.service() == RootStartupContext.Service.API
            ? ServiceConfigFiles.Service.API
            : ServiceConfigFiles.Service.WEB;
    var identities = new FixedServiceIdentity();
    long configGroup = identities.configurationGroup();
    var security = LinuxInodeSecurity.create();
    var io = new RootBatchCredentialReader.NativeIo();
    try (var database =
            InspectorDbCredential.consume(
                readSource(
                    context,
                    self,
                    service == ServiceConfigFiles.Service.API ? "db-api" : "db-web",
                    0,
                    configGroup,
                    security,
                    io));
        var ops =
            InspectorDbCredential.consume(
                readSource(context, self, "mq-ops", 0, configGroup, security, io))) {
      context.recheck(self);
      T result = Objects.requireNonNull(work.execute(database, ops));
      context.recheck(self);
      return result;
    }
  }

  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification =
          "SSC137 NOFOLLOW fixed host /etc ancestor, all observations close before secret decode")
  private static byte[] readSource(
      RootStartupContext context,
      RootStartupContext.Snapshot self,
      String fixedName,
      long group,
      long configGroup,
      InodeSecurityCalls security,
      RootBatchCredentialReader.Io io)
      throws IOException {
    context.recheck(self);
    var policy =
        new EnvironmentInodePolicy(
            security,
            new EnvironmentInodePolicy.Source() {
              public java.util.Map<String, Object> attributes(Path held) throws IOException {
                return io.attributes(held);
              }

              public String filesystem(Path held) throws IOException {
                return io.filesystem(held);
              }
            });
    byte[] material = new byte[65537];
    try {
      var calls = LinuxHostDirectoryCalls.create();
      Path path = Path.of("/etc");
      int count =
          ResourceScope.acquire(
              () -> OwnedTransferDirectory.open(calls, path),
              OwnedTransferDirectory::close,
              etc -> {
                var beforeEtc = etc.atDirectory(p -> policy.ancestor(p, false));
                require(!beforeEtc.readonly());
                int result =
                    ResourceScope.acquire(
                        () -> etc.openExistingChild("schubert-nk"),
                        OwnedTransferDirectory::close,
                        app -> {
                          var beforeApp =
                              app.atDirectory(
                                  p -> policy.snapshot(p, false, true, 0, 0, configGroup));
                          require(!beforeApp.readonly());
                          int length =
                              ResourceScope.acquire(
                                  () -> app.openExistingChild("credentials"),
                                  OwnedTransferDirectory::close,
                                  credentials ->
                                      readFixed(
                                          credentials,
                                          security,
                                          io,
                                          policy,
                                          fixedName,
                                          group,
                                          material));
                          require(
                              beforeApp.equals(
                                  app.atDirectory(
                                      p -> policy.snapshot(p, false, true, 0, 0, configGroup))));
                          return length;
                        });
                require(beforeEtc.equals(etc.atDirectory(p -> policy.ancestor(p, false))));
                return result;
              });
      context.recheck(self);
      return Arrays.copyOf(material, count);
    } finally {
      Arrays.fill(material, (byte) 0);
    }
  }

  static int readFixed(
      OwnedTransferDirectory root,
      InodeSecurityCalls security,
      RootBatchCredentialReader.Io io,
      EnvironmentInodePolicy policy,
      String fixedName,
      long group,
      byte[] material)
      throws IOException {
    Objects.requireNonNull(root);
    Objects.requireNonNull(security);
    Objects.requireNonNull(io);
    Objects.requireNonNull(policy);
    Objects.requireNonNull(fixedName);
    Objects.requireNonNull(material);
    require(material.length == 65537);
    require(security.effectiveUid() == 0 && !Thread.currentThread().isInterrupted());
    var directory = root.atDirectory(p -> policy.hostCredentialSource(p, true, 0));
    var before =
        root.atExistingEntryHandle(fixedName, p -> policy.hostCredentialSource(p, false, group));
    require(before.metadata().device() == directory.metadata().device());
    int count =
        root.atExistingEntryHandle(
            fixedName,
            p -> {
              require(before.equals(policy.hostCredentialSource(p, false, group)));
              int length =
                  ResourceScope.acquire(
                      () -> io.open(p),
                      SeekableByteChannel::close,
                      channel -> {
                        require(channel.size() == before.metadata().size());
                        ByteBuffer buffer = ByteBuffer.wrap(material);
                        boolean eof = false;
                        while (buffer.hasRemaining()) {
                          require(
                              security.effectiveUid() == 0
                                  && !Thread.currentThread().isInterrupted());
                          int position = buffer.position();
                          int remaining = buffer.remaining();
                          int n = channel.read(buffer);
                          if (n == -1) {
                            require(buffer.position() == position);
                            eof = true;
                            break;
                          }
                          require(n > 0 && n <= remaining && buffer.position() == position + n);
                        }
                        require(
                            eof
                                && buffer.position() == before.metadata().size()
                                && channel.size() == before.metadata().size());
                        return buffer.position();
                      });
              require(before.equals(policy.hostCredentialSource(p, false, group)));
              return length;
            });
    require(
        before.equals(
            root.atExistingEntryHandle(
                fixedName, p -> policy.hostCredentialSource(p, false, group))));
    require(directory.equals(root.atDirectory(p -> policy.hostCredentialSource(p, true, 0))));
    return count;
  }
}
