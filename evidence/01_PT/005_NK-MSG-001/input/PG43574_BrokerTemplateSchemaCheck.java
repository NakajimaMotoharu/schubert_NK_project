import java.nio.file.Path;
import javax.xml.XMLConstants;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.validation.SchemaFactory;
import org.w3c.dom.Element;
import org.xml.sax.SAXParseException;

/** Read-only Artemis template validation. Does not create an Artemis component. */
final class BrokerTemplateSchemaCheck {
  private BrokerTemplateSchemaCheck() {}

  public static void main(String[] args) throws Exception {
    if (args.length != 2) {
      throw new IllegalArgumentException("expected fixed schema and template inputs");
    }
    var schemas = SchemaFactory.newInstance(XMLConstants.W3C_XML_SCHEMA_NS_URI);
    schemas.setFeature(XMLConstants.FEATURE_SECURE_PROCESSING, true);
    schemas.setProperty(XMLConstants.ACCESS_EXTERNAL_DTD, "");
    schemas.setProperty(XMLConstants.ACCESS_EXTERNAL_SCHEMA, "file");
    var schema = schemas.newSchema(Path.of(args[0]).toFile());
    var validator = schema.newValidator();
    validator.setProperty(XMLConstants.ACCESS_EXTERNAL_DTD, "");
    validator.setProperty(XMLConstants.ACCESS_EXTERNAL_SCHEMA, "");
    var documents = DocumentBuilderFactory.newNSInstance();
    documents.setFeature(XMLConstants.FEATURE_SECURE_PROCESSING, true);
    documents.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
    documents.setAttribute(XMLConstants.ACCESS_EXTERNAL_DTD, "");
    documents.setAttribute(XMLConstants.ACCESS_EXTERNAL_SCHEMA, "");
    documents.setXIncludeAware(false);
    var document = documents.newDocumentBuilder().parse(Path.of(args[1]).toFile());
    validator.validate(new DOMSource(document));
    System.out.println("TRACKED_TEMPLATE_SCHEMA=PASS");

    String namespace = "urn:activemq:core";
    var firstQueue = document.getElementsByTagNameNS(namespace, "queue").item(0);
    Element invalidDurable = document.createElementNS(namespace, "durable");
    invalidDurable.setTextContent("invalid");
    firstQueue.insertBefore(invalidDurable, firstQueue.getFirstChild());
    try {
      validator.validate(new DOMSource(document));
      throw new IllegalStateException("invalid durable value was accepted");
    } catch (SAXParseException expected) {
      System.out.println("INVALID_DURABLE_SCHEMA=REJECTED");
    }
  }
}
