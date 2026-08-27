# Today in AI Scheduled Task Context

Updated: August 26, 2026

## Approved Triggers

Run when the standalone Codex scheduled task `today-in-ai` starts or when Payton manually asks for the current day's Today in AI post. Determine the date in `America/New_York`.

## Approved Publishing Policy

The scheduled run or manual daily request authorizes the complete workflow and immediate publishing after all required gates pass. Do not ask for a second confirmation.

## Required Route

Create and submit LinkedIn and X posts through `execution/social_publisher.py` and Postiz. YouTube is not part of the Today in AI posting process.

## Copy Format

- Same exact copy and image on LinkedIn and X
- Public copy contains no URLs, `Sources:` footer, citation list, or source links; research evidence stays in `sources.md`
- Normal platform text
- No Markdown bold
- No Unicode lookalike bold
- `Today in AI: <Month Day>` on the first line
- Each story heading in title case on its own line with a colon
- Full blank line after the title, every heading, and every sentence or short thought
- One or two stories by default, three when the evidence earns them, and four only on an exceptional day

## Required Safety Behavior

- Never publish an unverifiable claim.
- Never publish without the final image.
- Never publish until the rolling seven-day novelty review passes.
- Never reuse a story angle, image hook, meme family, main visual composition, subject pose, or visual joke from the previous seven calendar days.
- Use a real recognizable established meme or directly relevant public-figure asset when its premise fits. Do not replace it with an AI-generated generic person.
- Record visual and logo provenance in the dated `image-assets.json`, including source URLs, local hashes, and an accurate usage note.
- Use reference-aware generation for face, expression, costume, prop, and logo transformations, or a professionally integrated background-removed cutout.
- Use only the AI Mentorship designed palette and heavy phone-readable type.
- Supply current official company and product logos as image references. Never ask a model to invent or approximate them, and repair any fidelity error with the exact source asset.
- Require every in-scene logo to remain fully inside its intended physical surface and follow that surface's plane. On a keyboard, the full mark must stay inside the keycap's top face without crossing the bevel or gaps.
- Add exact headline type after the base visual is approved.
- Apply the transparent Today in AI master with `execution/today_in_ai_badge.py` at exactly 230 pixels wide and 84 pixels from the left and bottom.
- Never announce importance with `this matters`, `that matters`, or a close variation. State the consequence directly.
- Never end with `only time will tell`, `welcome to the future`, `we're just getting started`, `one thing is clear`, a branded signoff, or a detached joke kicker.
- Never copy Fireship wording, nicknames, catchphrases, exact analogies, sponsor language, or compositions. Transfer only the event-to-mechanism and packaging mechanisms in the local reference library.
- A repeated company or topic is allowed only after a meaningful new event, and the copy must state exactly what changed.
- Never switch away from Postiz after a failure.
- Never retry a possibly successful submission until receipts and Postiz state are checked.
- Never treat one-platform partial success as a complete run.

## Rolling Novelty And Retention

Before research, run `execution/today_in_ai_novelty.py` for the current date and inspect only the previous seven calendar days. Open every listed final image. After the candidate copy, sourced visual, structured asset manifest, hook, and image exist, run the asset validator and novelty check. Revise any failed or repeated editorial or visual concept before packaging.

After LinkedIn and X are both verified, run `execution/today_in_ai_retention.py --apply`. The script acts only once every 14 days and moves dated Desktop delivery copies outside the rolling seven-day window to macOS Trash. It never removes workspace editions, images, logs, manifests, results, or receipts.

## Existing Successful Reference

The July 23, 2026 edition was approved, published, and verified on LinkedIn and X. Its files under `today-in-ai/editions/2026-07-23/`, `today-in-ai/images/2026-07-23/`, and `outputs/social-publisher/` are the working reference for package and manifest structure. Its Unicode-bold copy is historical and must not be reused as the future formatting standard.

The July 24, 2026 edition is the current formatting and production reference. It used normal text, four primary-source-verified stories, a final 1920 by 1080 image, separate Postiz submissions, verified platform release IDs, and one post per platform.

## Current And Retired Schedulers

The approved automation is active in ChatGPT desktop Scheduled as `today-in-ai`. It runs as a standalone Codex task in the local Business Vibe Coding project, starts a new chat per run, and uses the daily 8:00 AM America/New_York schedule.

The former 8:00 AM production trigger and 9:20 AM recovery trigger were unloaded and retired July 25, 2026. The installed plist was removed from `~/Library/LaunchAgents/`.

The source plist, runner, status files, and logs remain as history and a rollback path. Do not reinstall or load launchd while the ChatGPT desktop task is the approved replacement.
