package dev.codex.schubert.nk.protocol.layout.semantic;

/** MEDIA1024 descriptor MIME allowlist. Trace: UI 235/237, SS 333, SSC-004, PT-PRO-001-T04. */
public enum MediaMimeType implements WireEnum {
  AUDIO_MP4("audio/mp4"),
  AUDIO_MPEG("audio/mpeg"),
  AUDIO_OGG("audio/ogg"),
  AUDIO_WAV("audio/wav"),
  AUDIO_FLAC("audio/flac"),
  VIDEO_MP4("video/mp4");

  private final String wireValue;

  MediaMimeType(String wireValue) {
    this.wireValue = wireValue;
  }

  @Override
  public String wireValue() {
    return wireValue;
  }
}
