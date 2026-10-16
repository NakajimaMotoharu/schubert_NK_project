"""BUG1354: compare all property VALUES independently, not systemctl display ordering."""
import ast
import inspect
import pg4406_verified_shared_manager_cost as previous
from pg4060_original_profile_dual_stack import once

SLOT = 'pg4408-canonical-shared-manager-cost-v1'
CANONICAL = r'''
  private static byte[] canonical(String phase, byte[] raw) {
    if(!phase.equals("productionChildUnitRead"))return raw;
    for(byte b:raw)if(b!=10&&(b<32||b>126))throw new IllegalStateException("ASCII property required");
    String[] lines=new String(raw,java.nio.charset.StandardCharsets.US_ASCII).split("\n",-1);
    if(lines.length!=8||!lines[7].isEmpty())throw new IllegalStateException("exact seven values required");
    var values=new java.util.TreeMap<String,String>();
    for(int i=0;i<7;i++){
      int equals=lines[i].indexOf('=');
      if(equals<1||values.putIfAbsent(lines[i].substring(0,equals),lines[i].substring(equals+1))!=null)
        throw new IllegalStateException("duplicate/malformed property");
    }
    if(!values.keySet().equals(java.util.Set.of("Id","LoadState","ActiveState","SubState","MainPID","InvocationID","ControlGroup")))
      throw new IllegalStateException("complete fixed fields required");
    var result=new StringBuilder();values.forEach((k,v)->result.append(k).append('=').append(v).append('\n'));
    return result.toString().getBytes(java.nio.charset.StandardCharsets.US_ASCII);
  }
'''


def payload():
    raw = previous.payload()
    raw = once(raw, 'SLOT=' + repr(previous.SLOT), 'SLOT=' + repr(SLOT))
    node = next(n for n in ast.parse(raw).body if isinstance(n, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == 'JAVA' for t in n.targets))
    old = ast.literal_eval(node.value)
    new = once(old, '  private static String measure(', CANONICAL + '\n  private static String measure(')
    new = once(new, '.digest(expected)', '.digest(canonical(phase,expected))')
    return once(raw, 'JAVA=' + repr(old), 'JAVA=' + repr(new))


def main():
    transport = previous.previous.previous.previous.previous
    ns = {**vars(transport), 'SLOT': SLOT, 'payload': payload}
    exec(compile(inspect.getsource(transport.main), '<all fixed property values canonical ABBA>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    main()
