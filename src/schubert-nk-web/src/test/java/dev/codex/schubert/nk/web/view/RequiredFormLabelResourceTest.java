package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.regex.Pattern;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.junit.jupiter.api.Test;

/** UI222 §4–5, UI224/225, SS313, PT-WEB-FORM-LABEL001..005. */
final class RequiredFormLabelResourceTest {
  private static final String REQUIRED = "required";
  private static final String CONFIRM = "input[name=confirm]";
  private static final String ROLE = "select[name=role]";
  private static final String PASSWORD = "input[name=password]";
  private static final String PASSWORD_CONFIRM = "input[name=password_confirmation]";
  private static final String WARNING = ".destructive-secondary";

  @Test
  void questionInputIdentifiesTheRequiredTextarea() throws IOException {
    var document = template("questions/new");
    assertRequired(document, "label[for=question]", "textarea#question");
  }

  @Test
  void userCreationIdentifiesEveryRequiredVisibleInput() throws IOException {
    var document = template("admin/user-new");
    for (String control :
        new String[] {
          "input[name=username]", PASSWORD, PASSWORD_CONFIRM, ROLE, "select[name=enabled]"
        }) {
      assertWrappedRequired(document, control);
    }
  }

  @Test
  void newUpdateFormsIdentifyRequiredChoicesAndConfirmations() throws IOException {
    var user = template("admin/user-detail");
    for (String control : new String[] {ROLE, PASSWORD, PASSWORD_CONFIRM, CONFIRM}) {
      assertWrappedRequired(user, control);
    }
    assertWrappedRequired(template("notifications/detail"), CONFIRM);
    assertWrappedRequired(template("questions/detail"), CONFIRM);
  }

  @Test
  void cancelledAndDeletedActionsUseAWarningButtonOnlyInTheExistingConfirmationForm()
      throws IOException {
    assertWarningSubmit(template("notifications/detail"), ".cancel-form", "処理を取り消す");
    assertWarningSubmit(template("questions/detail"), ".delete-form", "質問・回答を削除");
    assertTrue(template("admin/user-new").select(WARNING).isEmpty());
    assertTrue(template("questions/new").select(WARNING).isEmpty());
  }

  @Test
  void warningButtonUsesTheApprovedRedForegroundAndLightBackground() throws IOException {
    try (var input =
        RequiredFormLabelResourceTest.class.getResourceAsStream("/static/css/schubert.css")) {
      assertNotNull(input);
      var css = new String(input.readAllBytes(), StandardCharsets.UTF_8);
      var declaration =
          Pattern.compile(Pattern.quote(WARNING) + "\\s*\\{([^}]*)}").matcher(css);
      assertTrue(declaration.find());
      var properties = declaration.group(1);
      assertTrue(
          Pattern.compile("(?:^|;)\\s*color\\s*:\\s*#8a1c1c\\s*;").matcher(properties).find());
      assertTrue(
          Pattern.compile("(?:^|;)\\s*background\\s*:\\s*#fdecec\\s*;").matcher(properties).find());
    }
  }

  private static void assertWarningSubmit(Document document, String form, String label) {
    var scope = document.select("form" + form + "[method=post]");
    assertEquals(1, scope.size(), form);
    var button = scope.select("button[type=submit]" + WARNING);
    assertEquals(1, button.size(), form);
    assertEquals(label, button.text(), form);
    assertEquals(1, scope.select(CONFIRM + "[required]").size(), form);
  }

  private static void assertWrappedRequired(Document document, String control) {
    assertRequired(document, "label:has(" + control + ")", control);
  }

  private static void assertRequired(Document document, String label, String control) {
    var labels = document.select(label);
    var controls = document.select(control);
    assertEquals(1, labels.size(), label);
    assertEquals(1, controls.size(), control);
    assertTrue(labels.text().contains("必須"), label);
    assertTrue(controls.hasAttr(REQUIRED), control);
  }

  private static Document template(String name) throws IOException {
    try (var body =
        RequiredFormLabelResourceTest.class.getResourceAsStream("/templates/" + name + ".html")) {
      assertNotNull(body, name);
      return Jsoup.parse(body, "UTF-8", "");
    }
  }
}
