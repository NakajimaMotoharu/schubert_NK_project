import java.util.*;
/** BUG722 private controlled snapshot Map text: order-independent, never drops fields/values. */
public final class Pg466MapText {
  static void require(boolean b){if(!b)throw new IllegalArgumentException("snapshot map syntax");}
  static String canonical(String text){
    require(text!=null && text.length()<=1048576);var out=new StringBuilder();
    for(int n=0;n<text.length();n++){
      char c=text.charAt(n);require(c!='}');
      if(c!='{'){out.append(c);continue;}
      int depth=1,end=n+1;
      for(;end<text.length() && depth>0;end++){char x=text.charAt(end);if(x=='{')depth++;if(x=='}')depth--;require(depth<=16);}
      require(depth==0);out.append(map(text.substring(n+1,end-1)));n=end-1;
    }return out.toString();
  }
  static String map(String body){
    var values=new TreeMap<String,String>();int start=0,curly=0,square=0;
    for(int n=0;n<=body.length();n++){
      if(n==body.length() || (body.charAt(n)==',' && curly==0 && square==0)){
        String e=body.substring(start,n);if(!e.isEmpty()){
          int at=e.indexOf('=');require(at>=0 && at<e.length()-1);String key=e.substring(0,at);
          require(key.matches("[a-zA-Z0-9_./-]*") && values.putIfAbsent(key,canonical(e.substring(at+1)))==null);
        }else require(body.isEmpty());
        if(n<body.length()){require(n+1<body.length() && body.charAt(n+1)==' ');n++;}start=n+1;
      }else{char c=body.charAt(n);if(c=='{')curly++;if(c=='}')curly--;if(c=='[')square++;if(c==']')square--;require(curly>=0 && square>=0);}
    }
    require(curly==0 && square==0);var result=new StringJoiner(", ","{","}");values.forEach((k,v)->result.add(k+"="+v));return result.toString();
  }
}
