# Template maintenance

Run `python3 -m unittest discover -s tests -v` from the repository for changed
asset, packaging or publication guards. Tests use local generic fixtures and
mocked publisher calls; never publish a test post to validate a template.

For each real run, check source evidence, schema 3, novelty, the packaging dry-run,
single-post X payload, account identity and route-specific readiness. Confirm
terminal status and independent destination evidence before marking publication.
Preserve journals when a call fails or times out; reconcile before any retry.

Version useful public changes and inspect privacy and links before publication.
Read back the commit-pinned files and release after pushing. A private source
change triggers a scoped review, not an automatic copy of the source or archive.
