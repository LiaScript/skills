# German texts, stylesheet in <head> and capitalized filter labels for the
# page of `liaex -f project` (the exporter writes fixed English texts).
# Usage after the build:  sed -i -f translate-de.sed index.html   (GNU sed)
s|</head>|<link rel="stylesheet" href="theme.css"></head>|
s/<html>/<html lang="de">/
s/All categories/Alle Themen/
s/Download \.\.\./Herunterladen/g
s/>xAPI Package</>xAPI-Paket</g
s/>H5P Package</>H5P-Paket</g
s/Search courses and sections…/Kurse und Abschnitte durchsuchen…/g
s/Search (Ctrl+K)/Suche (Strg+K)/g
s/(Ctrl+K)/(Strg+K)/g
s/Start typing to search…/Suchbegriff eingeben…/g
s/No results found\./Keine Treffer./g
s/↑ Top/↑ nach oben/g
s/aria-label="Go to top"/aria-label="Nach oben"/g
s/\(<option value="[^"]\+">\)\(.\)/\1\u\2/g
