public final class Pg466MapTextTest {
  static int count;
  static void check(boolean b){count++;if(!b)throw new AssertionError("map vector "+count);}
  public static void main(String[] args){
    check(Pg466MapText.canonical("{b=2, a=1}").equals("{a=1, b=2}"));
    check(Pg466MapText.canonical("{assets={/b={uid=0, gid=1}/abcd, /a={gid=1, uid=0}}, z=Data[rows=1, digest=abcd]}").equals("{assets={/a={gid=1, uid=0}, /b={gid=1, uid=0}/abcd}, z=Data[rows=1, digest=abcd]}"));
    check(Pg466MapText.canonical("{={uid=0}, a=1}").equals("{={uid=0}, a=1}"));
    check(!Pg466MapText.canonical("{a=1, b=2}").equals(Pg466MapText.canonical("{a=1}")));
    check(!Pg466MapText.canonical("{a=1, b=2}").equals(Pg466MapText.canonical("{a=1, b=3}")));
    check(!Pg466MapText.canonical("{a={x=1}/hash1}").equals(Pg466MapText.canonical("{a={x=1}/hash2}")));
    check(Pg466MapText.canonical("{}").equals("{}"));
    for(String bad:new String[]{"{a=1, a=1}","{a=1,b=2}","{a=1, }","{a=}","{a}","{a={x=1, x=2}}","{a=1","a=1}","{a=Data[rows=1}","{a=x]}"}){
      try{Pg466MapText.canonical(bad);throw new AssertionError("invalid accepted");}catch(IllegalArgumentException expected){check(true);}
    }
    try{Pg466MapText.canonical(null);throw new AssertionError("null accepted");}catch(IllegalArgumentException expected){check(true);}
    System.out.println("PG466_MAP_ORACLE_PASS independentAssertions="+count+" productionPT0=true mutation0=true");
  }
}
