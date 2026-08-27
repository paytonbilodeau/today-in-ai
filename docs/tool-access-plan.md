# Today in AI Tool Access Plan

## Required

- Headless Codex CLI using the current configured most-capable model
- Web research and official source access
- X profile and status research through `.agents/skills/x-youtube-research/SKILL.md`
- Gmail connector access to `hi@paytonbilodeau.com` for full-edition AI newsletter research and mailbox-wide recurring-sender discovery
- Local `yt-dlp` for public Fireship catalog, subtitle, metadata, and thumbnail refreshes
- Built-in Codex image generation
- Workspace read and write access
- Desktop delivery-folder write access
- `execution/text_readability.py`
- `execution/today_in_ai_novelty.py`
- `execution/today_in_ai_assets.py`
- `execution/today_in_ai_badge.py`
- `execution/today_in_ai_retention.py`
- `execution/today_in_ai_prepare.py`
- `execution/fireship_reference_scrape.py`
- `execution/social_publisher.py`
- Postiz credentials stored outside the workspace
- Postiz account aliases `linkedin` and `x`

## Publishing Workaround

Use Postiz for LinkedIn and X. Public copy must be link-free so X remains on the Postiz route; keep research URLs only in `sources.md`. YouTube is not part of the Today in AI posting process.

Preflight both Postiz routes before publishing. If either route is unavailable, preserve the complete package, append a failed-run record, and stop before publishing.

If one destination fails after the other is verified, preserve the successful result and repair only the missing destination after checking its receipt and Postiz state. Never submit a verified destination again.

## Browser Boundary

A browser may inspect or verify a delayed Postiz result. It may not create, edit, or publish LinkedIn or X posts. No browser publishing step is required.

## Local Novelty And Cleanup

The novelty review reads only the seven previous dated workspace editions and their final images. The asset validator reads only dated source files, official logo files, hashes, source URLs, the exact AI Mentorship palette, the production route, and the publication mark. The badge script applies the transparent master at locked geometry with local FFmpeg. None of these local checks requires a paid service or external database.

The retention script may move only exact `Today in AI - YYYY-MM-DD` directories under `~/Desktop/Leverage/Today in AI/` to macOS Trash. It may run only after LinkedIn and X are both verified and only when its 14-day state gate is due. It must not touch the workspace audit history.

## Secret Handling

Load no credentials from the workspace. Use the existing owner-only Postiz credential and account-map files under Payton's home directory.
