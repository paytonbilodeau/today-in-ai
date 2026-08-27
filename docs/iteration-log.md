# Today in AI Iteration Log

## 2026-08-26 LinkedIn And X Only

- Removed YouTube from the Today in AI posting process at Payton's request.
- Future scheduled and manual runs publish and verify only LinkedIn and X through Postiz.
- Removed the YouTube browser preflight, native posting step, LF and visual-spacing checks, three-destination completion gate, and YouTube-dependent retention gate from the active prompt, SOP, setup, context, maintenance, and shared memory files.
- Kept the daily 8:00 AM America/New_York schedule, local project, model, reasoning setting, editorial gates, image gates, packaging, and two-platform publishing authorization unchanged.
- Existing YouTube posts and historical run records remain untouched.

## 2026-08-24 Link-Free Public Copy And Required YouTube Publication

- Moved every research URL and citation to `sources.md`; all future LinkedIn, X, and YouTube public copy is link-free with no `Sources:` footer or citation list.
- Added a deterministic `today_in_ai_prepare.py` gate for editions dated August 25, 2026 or later so source links cannot push X away from the Postiz route again.
- Made a staged YouTube composer an explicit failed state. The scheduled or manual trigger authorizes the final `Post` click, live-detail verification, and channel `Posts` spacing verification in the same run.
- Preserved destination-specific repair behavior: never resubmit a verified LinkedIn or X post while fixing another platform.

## 2026-08-15 Newsletter Desk And Fireship Humor Upgrade

- Moved newsletter research from a fixed sender lookup to a mailbox-wide sweep of every current AI briefing, digest, roundup, Substack, and relevant product or research newsletter in `hi@paytonbilodeau.com`.
- Confirmed the missing recurring editorial sources The AI Brief, AI with Remy, Ben's Bites, and Marcus on AI, alongside the existing TLDR AI, The Neuron, The Rundown AI, Superhuman, The AI Daily Brief, There's An AI For That, and Morning Brew sources.
- Required full-edition reading and a newsletter coverage table in `sources.md` with story choices, ordering, source links, mechanism, examples, caveats, and verification state. Subjects and snippets no longer count as newsletter review.
- Newsletter research and explanations may inform the edition after being rewritten, but distinctive wording and jokes cannot be copied and every material claim still needs primary evidence.
- Pushed the writing closer to Fireship's comic pace: one strong situational premise per suitable story, two to four funny lines in a normal edition, and permission for a sharper punchline, absurd comparison, escalating list, understatement, or one callback when the verified mechanism earns it.
- Preserved the hard humor boundaries around factual accuracy, copied material, victims, identity, illness, death, layoffs, personal harm, politics, and serious safety events.
- Kept the active schedule, project, publishing authorization, story-ranking gates, and all three platform verification requirements unchanged.

## 2026-07-24

- Incident: the 8:00 AM Codex process stalled while launchd treated it as background work and the display slept.
- Safety result: the process was stopped before publishing and no duplicate was created.
- Production result: the July 24 edition was researched, packaged, published, and verified once on LinkedIn and X.
- Runner change: interactive launchd priority, AC wake assertions, 70-minute timeout, 100-minute stale lock, heartbeat, JSON status, and failure notification.
- Schedule change: added a guarded 9:20 AM recovery trigger.
- Validation change: added a deterministic `--self-test` and an early verified-result gate.
- Skill repair: corrected invalid YAML quoting in both installed schedule-skill copies.
- Current outcome: self-test passes; source and installed plists match; launchd is loaded with interactive priority and both guarded calendar triggers; forced-run duplicate gate exits cleanly.

## 2026-07-24 Editorial and Image Feedback

- Keep the simple, direct, readable editorial approach from the July 24 edition.
- Apply the no-AI-slop skill to every draft and add a completeness pass. The final copy must use natural full sentences, cogent reasoning, useful connective tissue, and enough explanation to stand on its own.
- Use bold professional thumbnail type at weight 800 or higher. The verified installed fallback is Arial Black.
- Default human expressions to calm, capable, curious, or lightly amused. Avoid panic and doom when the story supports rational optimism.
- Use current official logo assets only.
- Plan logo surfaces before generation, then composite each logo with matching perspective, lighting, texture, grain, reflections, edge softness, and occlusion.
- Historical rule, superseded July 28: the Today in AI mark was treated like an in-scene logo. It is now a fixed bottom-left series badge.
- A logo that is accurate but looks pasted on fails image QA.

## 2026-07-25 ChatGPT Desktop Decision

- Approved automation surface: Codex in the ChatGPT desktop app.
- Task type: standalone scheduled task with a new chat for every run.
- Project mode: local Business Vibe Coding project, not a worktree.
- Schedule: daily at 8:00 AM America/New_York, including weekends.
- Shared workflow source: `automations/today-in-ai/today-in-ai-automation-prompt.md`.
- Manual current-day requests remain an equivalent trigger.
- Legacy launchd remains retired.
- Local-file runs still require the Mac to be powered on and the ChatGPT desktop app to be running.
- Creation result: active automation `today-in-ai`, using the local Business Vibe Coding project and medium reasoning.

## 2026-07-28 Fireship And Quality Upgrade

- Refreshed the Fireship audit against seven current Code Report thumbnails and three current comparison formats.
- Kept the existing research and fact-checking gates.
- Added a cohesion pass so stories read as connected explanations instead of compressed source notes.
- Replaced the generic-meme fallback with a sourced-asset rule: use the real recognizable meme asset when it fits.
- Added a machine-checked `image-assets.json` for visual source URLs, hashes, usage notes, structured novelty fields, heavy type, publication mark placement, and official logo provenance.
- Standardized the Today in AI master as a fixed bottom-left series badge.
- Added a non-writing `today_in_ai_prepare.py --dry-run` gate.
- Updated the active Codex desktop automation prompt. The retired launchd path remains retired.

## 2026-07-30 Reference-Driven Thumbnail And Writing Upgrade

- Opened the live Fireship channel, enumerated 80 current uploads, inspected 36 high-resolution thumbnails, and read 20 matching full transcripts.
- Documented how titles create the open loop while the thumbnail states the concrete event and uses a transformed subject, logo, costume, or prop to show the relationship.
- Added the mirrored `today-in-ai-thumbnail` skill for reference-aware generation, professional cutout compositing, semantic logo placement, factual satire, heavy type, and phone-size QA.
- Locked every designed color to the AI Mentorship palette while preserving natural source colors and exact official logo colors.
- Added `execution/today_in_ai_badge.py` so the transparent Today in AI master is always 230 pixels wide and 84 pixels from the left and bottom.
- Upgraded `image-assets.json` to schema version 2 with production route, palette, prompt, logo-fidelity, and badge-geometry gates. Schema version 1 remains readable for old editions.
- Added a writing gate against `this matters`, `that matters`, and other announced-importance phrasing. Each story must state the consequence directly in short, connected, complete prose.
- Updated the active `today-in-ai` desktop automation without changing its schedule, project, model, or publishing authorization.

## 2026-08-03 YouTube Community Distribution

- Added Payton's native YouTube Community feed as the third daily destination.
- Kept Postiz as the exclusive LinkedIn and X route because its YouTube integration requires a video attachment.
- Added a native signed-in YouTube preflight before any destination publishes.
- Made the YouTube Community text-only post the final publishing action, using the exact contents of `copy.txt` with no image.
- Added current-date duplicate detection, public `/post/<post-id>` exact-copy verification, partial-success repair behavior, and three-destination result logging.
- Moved the retention gate behind verified LinkedIn, X, and YouTube publication.
- Updated the authoritative shared prompt that the active `today-in-ai` task reads on every run without changing its 8:00 AM schedule, local project, model, or reasoning settings.
- The app rejected two attempts to refresh the task's embedded wrapper while this scheduled run was active. The embedded wrapper remains pending for metadata parity, but the authoritative shared prompt controls the next run's production and publishing behavior.

## 2026-08-04 Logo Surface And YouTube Posts Correction

- Payton approved leaving the August 4 edition unchanged but rejected the keyboard-logo integration for future editions because the marks did not belong to the keycap top faces.
- Added a hard surface-containment gate. Every visible logo pixel must remain on the intended usable surface and follow its plane. A keyboard logo must stay inside the keycap top face without crossing its bevel, wall, gaps, or neighboring keys.
- Replaced the `Your Community`, `My Community`, and Community activity route with the YouTube channel `Posts` publishing surface.
- YouTube verification now requires both an exact-copy public `/post/<id>` page and a visible listing in the public channel `Posts` tab.
- Kept the active schedule, project, and publishing authorization unchanged. The desktop API again rejected wrapper-only metadata updates, so the task continues to read the corrected shared prompt as authoritative. No duplicate automation was created.
