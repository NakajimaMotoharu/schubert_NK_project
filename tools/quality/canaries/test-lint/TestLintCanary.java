// Deliberately invalid lint fixture, never Production or an executed Test/Main.
import java.util.ArrayList;
import java.util.List;

final class TestLintCanary {
  List<String> value() {
    return new ArrayList();
  }
}
