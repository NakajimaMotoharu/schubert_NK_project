import com.google.gson.Strictness;
import com.google.gson.stream.JsonReader;
import com.google.gson.stream.JsonToken;
import java.io.IOException;
import java.io.StringReader;
import java.util.List;

/** Independent pinned-library contract study, not Production coverage or acceptance. */
public final class Pg2498GsonStrictEndContract {
  private Pg2498GsonStrictEndContract() {}

  private static JsonToken end(String text, Strictness strictness) throws IOException {
    try (var reader = new JsonReader(new StringReader(text))) {
      reader.setStrictness(strictness);
      reader.beginObject();
      while (reader.hasNext()) {
        reader.nextName();
        reader.nextString();
      }
      reader.endObject();
      return reader.peek();
    }
  }

  public static void main(String[] args) throws IOException {
    if (args == null || args.length != 0) throw new IllegalArgumentException("fixed vectors only");
    var valid = List.of("{}", "{} \t\r\n", "{\"literal\":\"ok\"}", "{\"literal\":\"ok\"}\n");
    var invalid =
        List.of(
            "{}{}",
            "{} []",
            "{} 1",
            "{} true",
            "{} null",
            "{} \"literal\"",
            "{} //comment",
            "{} /*comment*/",
            "{} \uFEFF",
            "{} ,",
            "{} #comment");
    for (String text : valid)
      if (end(text, Strictness.STRICT) != JsonToken.END_DOCUMENT)
        throw new AssertionError("strict EOF contract broken");
    int rejected = 0;
    for (String text : invalid) {
      try {
        end(text, Strictness.STRICT);
      } catch (IOException expected) {
        rejected++;
      }
    }
    if (rejected != invalid.size()) throw new AssertionError("strict trailing input accepted");
    if (end("{}{}", Strictness.LENIENT) != JsonToken.BEGIN_OBJECT
        || end("{} true", Strictness.LENIENT) != JsonToken.BOOLEAN)
      throw new AssertionError("independent lenient control failed");
    System.out.println(
        "PG2498 actualExit0 strictEOF4 trailingRejected11 lenientControls2 productionCoverage0");
  }
}
