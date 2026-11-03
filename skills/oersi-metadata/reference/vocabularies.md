# Controlled vocabularies for `metadata.yml`

All URIs checked against the published SKOS vocabularies (skohub, dini-ag-kim) and the OERSI importer on 2026-11-03. A URI that is not listed here must be looked up at the vocabulary page; never derive one from a pattern — neighbouring numbers belong to unrelated subjects.

## Subject: `about` — Hochschulfächersystematik

Prefix `https://w3id.org/kim/hochschulfaechersystematik/`. Browse: https://w3id.org/kim/hochschulfaechersystematik/scheme

Three levels: `n` + 1 digit = Fächergruppe, `n` + 2 digits = Studienbereich, `n` + 3 or 4 digits = Studienfach. Prefer the most specific fitting Studienfach; use a Studienbereich when the material covers the whole area.

**Fächergruppen** (there is no `n6`):

| id | de | en |
|---|---|---|
| n0 | Fachübergreifend | Interdisciplinary |
| n1 | Geisteswissenschaften | Humanities |
| n2 | Sport | Sports |
| n3 | Rechts-, Wirtschafts- und Sozialwissenschaften | Law, Economics and Social Sciences |
| n4 | Mathematik, Naturwissenschaften | Mathematics, Natural Sciences |
| n5 | Humanmedizin/Gesundheitswissenschaften | Human Medicine / Health Sciences |
| n7 | Agrar-, Forst- und Ernährungswissenschaften, Veterinärmedizin | Agriculture, Forestry, Nutrition, Veterinary Medicine |
| n8 | Ingenieurwissenschaften | Engineering |
| n9 | Kunst, Kunstwissenschaft | Art, Art Theory |

**Common subjects:**

| Subject | Studienbereich | Studienfach |
|---|---|---|
| Informatik / Computer Science | n71 | n079 |
| Mathematik / Mathematics | n37 | n105 |
| Physik / Physics | n39 (Physik, Astronomie) | **n0128** |
| Chemie / Chemistry | n40 | n032 |
| Biologie / Biology | n42 | n026 |
| Geowissenschaften / Geosciences | n43 | n039 |
| Elektrotechnik / Electrical Engineering | n64 | n048 |
| Maschinenbau / Mechanical Engineering | n63 | n104 |
| Ingenieurwesen allgemein / Engineering (general) | n61 | — |
| Medizin / Medicine | n49 | n107 |
| Psychologie / Psychology | n32 | n132 |
| Sozialwissenschaften / Social Sciences | n26 | n148 |
| Wirtschaftswissenschaften / Economics | n30 | n184 |
| Rechtswissenschaft / Law | n28 | n135 |
| Erziehungswissenschaft / Education | n33 | n052 |
| Geschichte / History | n05 | n068 |
| Germanistik / German Studies | n09 | n067 |
| Anglistik / English Studies | n10 | n008 |
| Philosophie / Philosophy | n04 | n127 |
| Kunstgeschichte, Kunstwissenschaft / Art History | n74 | n092 |
| Musikwissenschaft / Musicology | n78 | n114 |
| Musikerziehung / Music Education | n78 | n113 |

Interdisciplinary material: `n0`.

## Resource type: `learningResourceType` — HCRT

Prefix `https://w3id.org/kim/hcrt/`. Browse: https://w3id.org/kim/hcrt/scheme

| id | en | de |
|---|---|---|
| application | Software Application | Softwareanwendung |
| assessment | Assessment | Lernkontrolle |
| audio | Audio Recording | Audio |
| case_study | Case Study | Fallstudie |
| course | Course | Kurs |
| data | Data | Daten |
| diagram | Diagram | Diagramm |
| drill_and_practice | Drill and Practice | Übung |
| educational_game | Game | Lernspiel |
| experiment | Experiment | Experiment |
| image | Image | Abbildung |
| index | Reference Work | Nachschlagewerk |
| lesson_plan | Lesson Plan | Unterrichtsplanung |
| map | Map | Karte |
| portal | Web Portal | Portal |
| questionnaire | Questionnaire | Fragebogen |
| script | Script | Skript |
| sheet_music | Sheet Music | Musiknoten |
| simulation | Simulation | Simulation |
| slide | Presentation | Präsentation |
| text | Text | Textdokument |
| textbook | Textbook | Lehrbuch |
| video | Video | Video |
| web_page | Web Page | Webseite |
| worksheet | Worksheet | Arbeitsmaterial |
| other | Other | Sonstiges |

A LiaScript course is usually `course`; add `slide` if it is used as a presentation.

## Educational level: `educationalLevel`

Prefix `https://w3id.org/kim/educationalLevel/`. **OERSI's GitHub/GitLab/Codeberg importer does not read this field**; it is valid AMB and useful for other harvesters, so it may stay in the file.

| id | de | en |
|---|---|---|
| level_A | Hochschule | University (covers 6–8) |
| level_6 | Bachelor oder äquivalent | Bachelor or equivalent |
| level_7 | Master oder äquivalent | Master or equivalent |
| level_8 | Promotion oder äquivalent | Doctoral or equivalent |
| level_0 … level_3 | Elementar-, Primar-, Sekundarbereich I/II | early childhood … upper secondary |
| level_4 | Postsekundarer nicht-tertiärer Bereich (Berufliche Bildung) | post-secondary non-tertiary |
| level_5 | Kurzes tertiäres Bildungsprogramm | short-cycle tertiary |
| level_B | Vorbereitungsdienst | preparatory service |
| level_C | Fortbildung | advanced training |

`level_06` does not exist (an old AMB example uses it).

## Audience: `audience`

Prefix `http://purl.org/dcx/lrmi-vocabs/educationalAudienceRole/` (note `http`): `student`, `teacher`, `mentor`, `parent`, `peerTutor`, `professional`, `administrator`, `generalPublic`.

## Licenses OERSI accepts

Any other URL makes the record invalid and it is dropped.

| License | URL |
|---|---|
| CC0 | `https://creativecommons.org/publicdomain/zero/1.0/` |
| CC BY 4.0 | `https://creativecommons.org/licenses/by/4.0/` |
| CC BY-SA 4.0 | `https://creativecommons.org/licenses/by-sa/4.0/` |
| CC BY-NC, -ND, … | `https://creativecommons.org/licenses/<code>/4.0/` |
| GNU GPL/LGPL/FDL | `https://www.gnu.org/licenses/…` |
| Apache 2.0 | `https://www.apache.org/licenses/LICENSE-2.0` |
| MIT | `https://opensource.org/licenses/MIT` |
| BSD | `https://opensource.org/licenses/BSD-3-Clause` (or `BSD-2-Clause`) |

Write the canonical CC form: `https`, trailing slash, no `deed.de`/`legalcode` (OERSI normalises those, but other harvesters may not). Not accepted, for example: Free Art License, Unlicense, WTFPL, "all rights reserved".
