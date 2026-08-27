# Codex Scheduled Task Update Prompt

Update the existing Codex automation named `Today in AI` with Automation ID `today-in-ai`.

Keep its current schedule, timezone, project, model, reasoning setting, active state, and new-chat behavior. Publish only to LinkedIn and X through Postiz. YouTube is not part of the posting process and the run must not require browser-control or YouTube permissions.

Replace the scheduled-run instructions with the following:

```text
Run directly in `~/workspace`. This is a standalone scheduled run and must put the complete result in this run's new chat.

1. Determine the current date in `America/New_York`.
2. Read `AGENTS.md` and `automations/today-in-ai/today-in-ai-automation-prompt.md` completely. The shared prompt is authoritative.
3. Before research, check the current date's `publish-results.json`, local receipts, and Postiz state. If LinkedIn and X are already verified as published, stop without uploading or publishing. Never republish a verified destination.
4. Build the rolling seven-day novelty report, read it, and open every final image it lists. Do not inspect older editions.
5. Verify every material claim with the best primary source and an independent check when a company is grading itself.
6. Research the normal 36-hour window first. Scan official and reporting accounts on X, the AI newsletters in `hi@paytonbilodeau.com`, official AI newsrooms, and broad independent AI desks including Reuters Technology/AI, AP, TechCrunch AI, The Verge AI, and Ars Technica AI when current and accessible. Review at least twelve current leads across the combined surfaces, or document that fewer existed after all required surfaces were checked.
7. Build a weighted candidate slate in `sources.md` before choosing the edition. Score audience breadth and consequence plus capability/policy/economic/scientific step-change at x3, immediate availability and evidence strength at x2, and cross-source salience and novelty at x1. Apply the penalties in `directives/today_in_ai.md`. Freshness is eligibility, not importance. The highest consequential verified story must lead unless a specific evidence-based disqualification is recorded. Ask whether a well-informed AI reader would say the edition skipped the day's obvious biggest verified story; if yes, research and rank again.
8. Publish at least one accurate, relevant, previously uncovered AI story every calendar day. If no candidate clears the significance bar in the normal window, expand deliberately up to seven calendar days and choose the strongest verified unused story. Never use a story older than seven days. One story is acceptable on a slow day.
9. Write short, cogent, comprehensive prose. Connect event to mechanism to consequence, keep each limitation beside the claim it qualifies, and use full natural sentences. Apply the no-ai-slop and readability gates. Keep every research URL and citation in `sources.md`; public `copy.txt` must be link-free.
10. Read the current Fireship audit, `.agents/skills/today-in-ai-thumbnail/SKILL.md`, and the image templates named in the shared prompt. Use a real recognizable meme or directly relevant public-figure asset when its premise fits. Never replace it with a generic AI-generated person.
11. Build schema-version-2 `image-assets.json` with source URLs, local hashes, usage notes, production route, composition fields, the exact AI Mentorship palette, heavy phone-readable typography, locked badge geometry, and official logo sources. Supply official company and product logos as image references and never invent or approximate them.
12. Leave the bottom-left badge area empty during generation. Apply the transparent Today in AI master with `execution/today_in_ai_badge.py` at exactly 230 pixels wide, 84 pixels from the left, and 84 pixels from the bottom, with no backing plate.
13. Use a different hook, meme family, main composition, subject pose, prop setup, and visual joke from the rolling seven-day window. Run `execution/today_in_ai_assets.py`, the final novelty check with `--check`, and `execution/today_in_ai_prepare.py --dry-run`. Fix every failure before packaging. Never publish a failed candidate.
14. Treat this scheduled run as Payton's authorization to publish immediately after every required gate passes. Use the same exact copy and image on LinkedIn and X, publish each platform separately through `execution/social_publisher.py` and Postiz, and verify state, release ID, live URL, attached image, and receipt.
15. Write `publish-results.json` with verified LinkedIn and X platform records. Mark the run published only after both destinations are verified. Append the complete result to `today-in-ai/log.md` and copy the updated package and results into the dated Desktop delivery folder.
16. If any accuracy, source, importance-ranking, novelty, asset, image, account-routing, Postiz, publishing, or verification gate fails, preserve the dated package, append the exact failure and repair step to `today-in-ai/log.md`, and stop without switching routes.
17. Only after LinkedIn and X are both verified as published, run the 14-day retention gate. It may move only dated delivery folders outside the current seven-day window from `~/Desktop/Today in AI/` to macOS Trash. Never remove workspace editions, images, logs, manifests, results, or receipts.
18. Report the complete result in the scheduled-run chat, including the scored candidate slate and why the lead won, final copy, image path, delivery folder, asset and novelty results, retention result, both live URLs, and both verified platform states.

Do not open or publish to YouTube. Do not reinstall or invoke the retired launchd scheduler. Do not create a second recovery schedule.
```
