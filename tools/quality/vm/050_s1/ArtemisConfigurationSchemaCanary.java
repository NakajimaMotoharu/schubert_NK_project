import java.nio.file.Files;
import java.nio.file.Path;
import javax.xml.XMLConstants;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.validation.Schema;
import javax.xml.validation.SchemaFactory;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.xml.sax.SAXParseException;

/**
 * PT-QUALITY3390-001: official fixed XSD, independent valid/invalid DOM fixtures; no Broker start.
 */
public final class ArtemisConfigurationSchemaCanary {
  private static final String CORE = "urn:activemq:core";

  private ArtemisConfigurationSchemaCanary() {}

  public static void main(String[] args) throws Exception {
    if (args.length != 2) throw new IllegalArgumentException("template and fixed schema required");
    var factory = SchemaFactory.newInstance(XMLConstants.W3C_XML_SCHEMA_NS_URI);
    factory.setFeature(XMLConstants.FEATURE_SECURE_PROCESSING, true);
    factory.setProperty(XMLConstants.ACCESS_EXTERNAL_DTD, "");
    // Only the fixed adjacent xml.xsd import is read; no HTTP/network schema resolution.
    factory.setProperty(XMLConstants.ACCESS_EXTERNAL_SCHEMA, "file");
    var schema = factory.newSchema(Path.of(args[1]).toFile());
    var builder = DocumentBuilderFactory.newInstance();
    builder.setNamespaceAware(true);
    builder.setFeature(XMLConstants.FEATURE_SECURE_PROCESSING, true);
    builder.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
    builder.setAttribute(XMLConstants.ACCESS_EXTERNAL_DTD, "");
    builder.setAttribute(XMLConstants.ACCESS_EXTERNAL_SCHEMA, "");
    Document original;
    try (var input = Files.newInputStream(Path.of(args[0]))) {
      original = builder.newDocumentBuilder().parse(input);
    }
    validate(schema, core(original));
    for (String field :
        new String[] {"unknown-element", "journal-type", "max-disk-usage", "persistence-enabled"}) {
      var changed = (Document) original.cloneNode(true);
      if (field.equals("unknown-element")) {
        core(changed).appendChild(changed.createElementNS(CORE, "not-approved-configuration"));
      } else {
        var nodes = changed.getElementsByTagNameNS(CORE, field);
        if (nodes.getLength() != 1) throw new AssertionError("one fixed original field");
        nodes.item(0).setTextContent("invalid-schema-value");
      }
      boolean refused = false;
      try {
        validate(schema, core(changed));
      } catch (SAXParseException expected) {
        refused = true;
      }
      if (!refused) throw new AssertionError("official schema must refuse " + field);
      System.out.println("REJECTED " + field);
    }
    validate(schema, core(original));
    System.out.println("PASS original-before-and-after; independent-negative4; broker-start0");
  }

  private static Element core(Document document) {
    var nodes = document.getElementsByTagNameNS(CORE, "core");
    if (nodes.getLength() != 1) throw new AssertionError("one core element");
    return (Element) nodes.item(0);
  }

  private static void validate(Schema schema, Element element) throws Exception {
    var validator = schema.newValidator();
    validator.setProperty(XMLConstants.ACCESS_EXTERNAL_DTD, "");
    validator.setProperty(XMLConstants.ACCESS_EXTERNAL_SCHEMA, "");
    validator.validate(new DOMSource(element));
  }
}
