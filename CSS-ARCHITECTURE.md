# CSS architecture

`styles/site.css` is the single active source for the public stylesheet. The
release build copies this reviewed file to `_site/site.css` and never appends
CSS afterward.

The named section markers inside the file document the historical design
layers and make their order reviewable. They are not separate network requests
or separate build inputs. Root-level CSS files are retained temporarily as
legacy references, but production does not read them.

## Rules

- Make visual changes in `styles/site.css`.
- Do not append CSS in workflow steps or HTML transformation scripts.
- Keep every required section marker unique.
- Run `python verify-css-architecture.py` after CSS or build changes.
- Reduce legacy selector specificity only in visually reviewed batches; do not
  remove `!important` declarations globally.

The deployment workflow enforces these rules and compares the generated
stylesheet byte-for-byte with the canonical source.
