package dev.codex.schubert.nk.migration;

import java.security.NoSuchAlgorithmException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Five declared Current projections to six-table COPY values, never actual DB or asset admission.
 * NK-MIG-001; MIG003005006/MIG-DAT001002005/DAT004/TST; UI227242254; SS311331343 SSC402/408;
 * PT-MIG-CURRENTASSEMBLY001..022. Retains stored text, explicit source order and shared bindings.
 */
@NullMarked
public final class CurrentMigrationAssembler {
  private final ScenarioFileMigrationMap retainedFileIds;
  private final ScenarioEntryPlacementMap retainedEntryIds;
  private final SpeakerMigrationMap retainedSpeakers;
  private final CurrentScenarioFileMapper retainedFiles;
  private final CurrentScenarioEntryMapper retainedEntries;
  private final AudioMigrationMap retainedAudio;
  private final CurrentAudioLinkMapper retainedLinks;
  private final AssetMigrationManifest retainedMediaClaims;

  public CurrentMigrationAssembler(
      @Nullable ScenarioFileMigrationMap files,
      @Nullable ScenarioEntryPlacementMap placement,
      @Nullable SpeakerMigrationMap speakers,
      @Nullable List<AudioMigrationMap.@Nullable AudioMapping> audioMappings,
      @Nullable List<CurrentAudioLinkMapper.@Nullable LinkOrder> linkOrders,
      @Nullable AssetMigrationManifest assets,
      @Nullable String gameOneRoot,
      @Nullable String gameTwoRoot) {
    if (files == null
        || placement == null
        || speakers == null
        || audioMappings == null
        || linkOrders == null
        || assets == null) throw invalid();
    retainedFileIds = files;
    retainedEntryIds = placement;
    retainedSpeakers = speakers;
    retainedFiles = new CurrentScenarioFileMapper(files, assets, gameOneRoot, gameTwoRoot);
    retainedEntries = new CurrentScenarioEntryMapper(files, placement, speakers);
    retainedAudio = new AudioMigrationMap(audioMappings, assets, gameOneRoot, gameTwoRoot);
    retainedLinks = new CurrentAudioLinkMapper(placement, retainedAudio, linkOrders);
    var media = new ArrayList<AssetMigrationManifest.Entry>();
    for (var entry : assets.entries())
      if (entry.kind() == AssetMigrationManifest.Kind.VIDEO
          || entry.kind() == AssetMigrationManifest.Kind.MUSIC) media.add(entry);
    retainedMediaClaims = new AssetMigrationManifest(media);
  }

  public MigrationMasterCopyDataset assemble(
      CurrentMigrationProjection.@Nullable SourceSnapshot snapshot,
      @Nullable List<? extends @Nullable MediaAssetCopyRow> mediaRows,
      @Nullable Instant migratedAt) {
    if (snapshot == null || mediaRows == null || migratedAt == null) throw invalid();
    var speakers = retainedSpeakers.copyRows(snapshot.speakers(), migratedAt);
    var files = retainedFiles.copyRows(snapshot.files(), migratedAt);
    var entries = retainedEntries.copyRows(snapshot.entries(), migratedAt);
    var audio = retainedAudio.copyRows(snapshot.audio(), migratedAt);
    var links = retainedLinks.copyRows(snapshot.links(), entries, audio, migratedAt);
    var media =
        new MediaAssetCopyBatch(
            retainedMediaClaims, new ArrayList<@Nullable MediaAssetCopyRow>(mediaRows));
    var scenario = new ScenarioCopyDataset(files, entries);
    var content = new MigrationCopyDataset(scenario, links.audioRows(), links.linkRows(), media);
    return new MigrationMasterCopyDataset(speakers, content);
  }

  public CurrentMigrationMappingManifest mappingManifest() throws NoSuchAlgorithmException {
    return new CurrentMigrationMappingManifest(
        retainedFileIds, retainedEntryIds, retainedSpeakers, retainedAudio);
  }

  @Override
  public String toString() {
    return "CurrentMigrationAssembler[REDACTED]";
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("migration Current assembly input is invalid");
  }
}
