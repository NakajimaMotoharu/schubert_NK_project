package dev.codex.schubert.nk.protocol.layout;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import org.junit.jupiter.api.Test;

/** SS323354/SSC445/451: independent immutable registry bindings under bounded concurrent reads. */
class PayloadTypeCatalogStateContractTest {
  @Test // PT-PRO-CATALOG-STATE001
  void concurrentReadersRetainAllIndependentSixtyFourTypeBindings()
      throws IOException, InterruptedException, ExecutionException, TimeoutException {
    List<List<String>> inputRows = new ArrayList<>();
    try (var input = getClass().getResourceAsStream("/protocol/named-types-ss323.tsv")) {
      assertNotNull(input);
      try (var reader = new BufferedReader(new InputStreamReader(input, StandardCharsets.UTF_8))) {
        for (String line = reader.readLine(); line != null; line = reader.readLine()) {
          if (line.isBlank() || line.startsWith("#")) continue;
          String[] columns = line.split("\t", -1);
          assertEquals(3, columns.length);
          inputRows.add(List.of(columns[0], columns[1], columns[2]));
        }
      }
    }
    List<List<String>> rows = List.copyOf(inputRows);
    assertEquals(64, rows.size());
    List<String> expected =
        rows.stream().map(row -> row.get(0) + "/" + row.get(1) + "/" + row.get(2)).toList();
    CountDownLatch ready = new CountDownLatch(2);
    CountDownLatch start = new CountDownLatch(1);
    Callable<List<String>> readAll =
        () -> {
          ready.countDown();
          assertTrue(start.await(10, TimeUnit.SECONDS));
          List<String> result = new ArrayList<>();
          for (List<String> row : rows) {
            LayoutId layout = new LayoutId(row.get(0));
            String data = PayloadTypeCatalog.dataType(layout).getSimpleName();
            String record =
                PayloadTypeCatalog.recordType(layout).map(Class::getSimpleName).orElse("-");
            result.add(row.get(0) + "/" + data + "/" + record);
          }
          return List.copyOf(result);
        };
    var workers = Executors.newFixedThreadPool(2);
    try {
      var first = workers.submit(readAll);
      var second = workers.submit(readAll);
      assertTrue(ready.await(10, TimeUnit.SECONDS));
      start.countDown();
      assertEquals(expected, first.get(10, TimeUnit.SECONDS));
      assertEquals(expected, second.get(10, TimeUnit.SECONDS));
    } finally {
      start.countDown();
      workers.shutdownNow();
      assertTrue(workers.awaitTermination(10, TimeUnit.SECONDS));
    }
  }
}
