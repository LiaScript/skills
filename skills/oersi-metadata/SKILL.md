---
name: oersi-metadata
description: >
  Use when someone wants an Open Educational Resource (OER) on GitHub, GitLab or
  Codeberg listed in OERSI (Open Educational Resources Search Index), wants to
  create, update or check a `metadata.yml`, asks about AMB / schema.org / LRMI /
  KIM metadata for learning resources (subject, resource type, educational
  level, license URLs), or about the repository topic
  `open-educational-resources`. German triggers: "Kurs auf OERSI
  veröffentlichen", "metadata.yml erstellen", "OER-Metadaten",
  "Hochschulfächersystematik", "warum taucht mein Kurs nicht in OERSI auf".
license: CC0-1.0
---

# OERSI metadata for Git repositories

OERSI harvests public repositories on **GitHub, GitLab and Codeberg** that carry the topic `open-educational-resources` and a file **`metadata.yml` in the repository root** (default branch). Harvesting runs about daily. The importer turns the file into an AMB record (Allgemeines Metadatenprofil für Bildungsressourcen) and validates it; an invalid record is dropped silently.

Everything below was checked against OERSI's importer code, the OERSI schema and the KIM vocabularies on 2026-11-03.

## Hard requirements — the record is dropped without them

1. File name exactly `metadata.yml`. **`metadata.yaml` is never read** — rename an existing one.
2. `creativeWorkStatus: Published` in every record.
3. `name`.
4. Repository public, topic `open-educational-resources` set (GitLab also still accepts the old topic `Open Educational Resources`).
5. If present, `license` must be one OERSI accepts: Creative Commons/CC0, GNU, Apache, MIT or BSD (exact URLs in `reference/vocabularies.md`). Any other license (Free Art License, Unlicense, …) invalidates the record — tell the user OERSI cannot list it.
6. If present, `about` needs at least one Hochschulfächersystematik (or Schulfächer) URI, and `learningResourceType` at least one HCRT URI.

`id` falls back to `url`, then the GitHub Pages URL, then the repository URL — set it to the URL where learners open the material (for LiaScript: the `liascript.github.io/course/?…` link).

## Recommended fields (ask for them, but do not block)

`description`, `license`, `creator`, `inLanguage`, `about`, `learningResourceType`, `image`, `datePublished`, `keywords`, `publisher`; optionally `audience`, `conditionsOfAccess`, `hasPart`, `dateCreated`.

**Read by AMB, ignored by OERSI's Git importer**: `educationalLevel`. Keep it if the user wants it (other harvesters use it), but do not present it as needed for OERSI. **Not read at all**: `video`, `interactivityType`, `isAccessibleForFree` — leave them out (`isAccessibleForFree` is set by OERSI itself).

## Template

```yaml
'@context': https://schema.org/
creativeWorkStatus: Published
type: LearningResource

name: "Mechanik für Ingenieure"
description: >-
  Interaktiver LiaScript-Kurs zu Statik und Dynamik für das Bachelorstudium.
id: "https://liascript.github.io/course/?https://raw.githubusercontent.com/OWNER/REPO/main/README.md"
license: "https://creativecommons.org/licenses/by/4.0/"

creator:
  - givenName: "Maria"
    familyName: "Beispiel"
    id: "https://orcid.org/0000-0002-1825-0097"
    type: Person
    affiliation:
      name: "Technische Universität Dresden"
      id: "https://ror.org/042aqky30"
      type: Organization

inLanguage:
  - de
about:
  - "https://w3id.org/kim/hochschulfaechersystematik/n104"
  - "https://w3id.org/kim/hochschulfaechersystematik/n0128"
learningResourceType:
  - "https://w3id.org/kim/hcrt/course"
educationalLevel:
  - "https://w3id.org/kim/educationalLevel/level_6"
image: "https://img.youtube.com/vi/VIDEO_ID/hqdefault.jpg"
keywords:
  - Mechanik
  - LiaScript
datePublished: "2026-11-03"
```

This is the shape OERSI's own form writes (plain URI strings, `@context` and `type` as strings — the importer replaces both anyway). Objects `{id: …}` are accepted too. Omit fields you do not have; never write empty strings.

## Subject, type, level, license

Look up every URI in **`reference/vocabularies.md`** — never guess a number: neighbouring codes are unrelated subjects (`n33` is Erziehungswissenschaften, not Mathematik; Physik is `n0128`). Prefer the specific Studienfach; give 1–3 subjects; interdisciplinary is `n0`. Write CC licenses in the canonical form `https://creativecommons.org/licenses/by/4.0/` (no `deed.de`). If the subject or license is unclear, ask; suggest 2–4 candidate subjects.

A YouTube video can supply the preview `image`: `https://img.youtube.com/vi/VIDEO_ID/hqdefault.jpg` (`maxresdefault.jpg` is missing for some videos).

## Several resources in one repository

- **Parts of one course** (chapters, lectures): `hasPart`, each item an object with `id` (or `url`) and `name`; no `type`, plain strings are dropped.
- **Independent resources**: `metadata.yml` may be a YAML list of records, or include files with the non-standard `!include path/from/repo-root.yml`. Every record needs its own `creativeWorkStatus: Published`.
- **Wildcards (`!include courses/*.yml`) work on GitLab only.** On GitHub a wildcard include makes the **whole** file fail and nothing is listed; on Codeberg it only sees the repository root. On GitHub list every file explicitly (`examples/multiple-resources-metadata.yml`).

## Workflow

1. Collect what the user gave or what the repository shows (README header, LICENSE file, LiaScript header).
2. Write the draft `metadata.yml` with everything known.
3. List the missing required items separately from optional improvements; ask one short question if only a few are missing.
4. Check: `metadata.yml` name, `creativeWorkStatus: Published` in every record, accepted license URL, URIs from the reference file, valid YAML (quote strings with `:` or `#`), dates as `YYYY-MM-DD`, no empty values, no wildcard include on GitHub.
5. Tell the user the steps below.

## Steps to give the user every time

1. Put `metadata.yml` into the repository root on the default branch (rename `metadata.yaml`).
2. Make the repository public and add the topic `open-educational-resources` (GitHub: gear icon next to "About"; GitLab: Settings → General → Topics; Codeberg: repository settings).
3. OERSI picks it up within about a day. For an immediate check, use the (experimental) re-import form https://oersi.org/pages/en/record_update/ with the repository URL (GitHub and GitLab).
4. The official form https://oersi.gitlab.io/metadata-form/metadata-generator.html can open and edit the file later.

Examples: `examples/minimal-metadata.yml`, `examples/full-metadata-multilingual.yml`, `examples/multiple-resources-metadata.yml`. A real indexed LiaScript course: https://raw.githubusercontent.com/TUBAF-IfI-LiaScript/VL_Softwareentwicklung/master/metadata.yml
