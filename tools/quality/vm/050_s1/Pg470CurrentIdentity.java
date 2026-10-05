import java.nio.file.Path;
import java.util.Map;

/** Fixed D3 identity bridge only. Normal completion is separately proved by the new owned tool. */
public final class Pg470CurrentIdentity {
  static final String SOURCE="d3bba6db6eb9fec13e4847a10541cf337f575731";
  static final String DIGEST="cc5e4dd7ca70d3a21e1145dd35b9f047856c4ab83bfac6f11722663ba7744462";
  static final Path BEFORE=Path.of("/var/lib/pgpt-s1-preservation/pg469-completed-deploy");
  static Map<String,String> show(String unit)throws Exception{return Pg469CurrentReadback.show(unit);}
  static void peer(String unit,long pid,String invocation)throws Exception{Pg469CurrentReadback.peer(unit,pid,invocation);}
  private Pg470CurrentIdentity(){}
}
