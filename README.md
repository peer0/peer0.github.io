# Joonghyuk Hahn · Academic Website

Personal academic website of Joonghyuk Hahn, postdoctoral researcher at Linköping University (Trustworthy Systems Group, RESIST).
Live at [peer0.github.io](https://peer0.github.io).

The site is plain HTML, CSS and JavaScript served by GitHub Pages. No build service is needed at deploy time.

## Pages

- `index.html`: introduction, current work, research directions, selected work, updates
- `publications.html`: full list with search, year, type and topic filters, and plain-text references
- `cv.html` and `Joonghyuk_Hahn_CV.pdf`: curriculum vitae
- `contact.html`: email, research profiles, affiliation

## Updating content

The HTML is generated from two data files. Edit the data, then rebuild.

| What | File |
| --- | --- |
| Name, email, affiliation, Now statement, news, projects | `data/site.json` |
| Papers (title, authors, venue, year, type, topic, links) | `data/publications.json` |
| Page structure | `scripts/build.py` |
| Colors, type, layout | `assets/style.css` |
| Menu, filters, reference copy | `assets/site.js` |
| Research illustrations | `assets/research/` |

```bash
python3 scripts/build.py          # regenerate HTML, sitemap.xml, robots.txt
python3 scripts/build.py --check  # confirm generated files match the data
```

The downloadable CV is compiled from the LaTeX source in `cv/full.tex` (kept locally, not published) and copied to `Joonghyuk_Hahn_CV.pdf`.
`scripts/build_cv.py` is an older generator; running it overwrites the PDF.

Paper `type` is one of `conference`, `journal`, `preprint`. Paper `topic` is one of `verification`, `code`, `language`, `formal`.
A `*` after an author name marks equal contribution. Selected work on the home page follows `selected_ids` in `data/site.json`.

## Credits

Fonts: [Newsreader](https://fonts.google.com/specimen/Newsreader) and [Manrope](https://fonts.google.com/specimen/Manrope), SIL Open Font License 1.1 (license texts in `assets/fonts/`).
Site source is released under the MIT License.
