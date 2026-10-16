package dev.codex.schubert.nk.batch.platform;

import dev.codex.schubert.nk.bootstrap.ChildStartupContext;
import dev.codex.schubert.nk.bootstrap.FixedServiceIdentity;
import java.io.IOException;
import java.util.List;
import java.util.UUID;

/** BUG1332 readonly fixed manager/identity/socket primitives. No HTTP, fake Root or authority. */
public final class RootPeerReadProfile {
  private RootPeerReadProfile() {}
  public static void main(String[] args) throws IOException {
    if (args.length != 0) throw new IllegalArgumentException("fixed peer diagnostic");
    for (int i = 0; i < 3; i++) {
      long at = System.nanoTime();
      byte[] raw = new InspectorUnitProbe.NativeReader().execute(List.of("/usr/bin/systemctl",
          "--system", "--no-pager", "--no-ask-password", "show",
          "--property=Id,LoadState,ActiveState,SubState,MainPID,InvocationID,Job,Type,Restart,KillMode,SendSIGKILL,NoNewPrivileges,CapabilityBoundingSet,AmbientCapabilities,User,Group,SupplementaryGroups,TimeoutStartUSec,TimeoutStopUSec,ExecStartPre,ExecStart,Result,ExecMainCode,ExecMainStatus,ExecMainStartTimestampMonotonic,ExecMainExitTimestampMonotonic",
          "caddy.service"), 8192);
      if (raw.length == 0) throw new IOException("manager projection absent");
      report("caddy-manager", at);
      at = System.nanoTime();
      var child = new ChildStartupContext().verifyCaddy(
          UUID.fromString("79a3260a-e16d-42bf-942a-b914ed144c28"),
          "a0c7fb91c4da42f09faec0f065a87767", new FixedServiceIdentity().resolveCaddy());
      if (child.pid() != 761848) throw new IOException("ordinary Caddy generation changed");
      report("caddy-identity", at);
      at = System.nanoTime();
      if (new MorningServiceReadiness.NativeIo(758821, 8091).sockets().isEmpty())
        throw new IOException("ordinary API listener absent");
      report("api-sockets", at);
      at = System.nanoTime();
      if (new MorningServiceReadiness.NativeIo(759868, 8081).sockets().isEmpty())
        throw new IOException("ordinary Web listener absent");
      report("web-sockets", at);
    }
  }
  private static void report(String phase, long at) {
    System.out.println("READONLY_PROFILE1 phase=" + phase + " count=1 nanos=" + (System.nanoTime() - at));
  }
}
