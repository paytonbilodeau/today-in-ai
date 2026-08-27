# ROLE AND TASK

Run the complete Today in AI workflow for the current date in `America/New_York`. Research the few consequential AI stories, verify each material claim, write a short plain-language edition, create one final 16:9 image, and publish the same copy and image to LinkedIn and X through Postiz. Verify both results and log the run. YouTube is not part of this workflow.

This file is the shared production packet for the standalone Today in AI scheduled task in Codex in the ChatGPT desktop app and for a user-requested manual run. Either trigger authorizes immediate publishing after every required gate passes.

# BUSINESS CONTEXT

Today in AI is Payton Bilodeau's daily AI briefing. It is concise, accurate, rationally optimistic, understandable to non-technical adults, and funny without weakening the reporting. Its pacing and humor should feel closer to Fireship: fast, specific, mischievous, and occasionally bold when the verified situation earns it.

# AUDIENCE OR USER

Write for intelligent adults aged 30 to 60+ who are curious about AI but do not follow technical news closely.

# WHEN THIS RUNS

Run when the standalone ChatGPT desktop scheduled task starts or when Payton asks for the current day's Today in AI post. Determine the date in `America/New_York`.

# INPUTS TO CHECK

Work inside `~/workspace`.

Read these files completely before working:

1. `AGENTS.md`
2. `automations/today-in-ai/business-profile.md`
3. `automations/today-in-ai/automation-roi-scorecard.md`
4. `automations/today-in-ai/decomposition-today-in-ai.md`
5. `automations/today-in-ai/context/today-in-ai-context.md`
6. `automations/today-in-ai/tool-access-plan.md`
7. `automations/today-in-ai/today-in-ai-scheduled-config.md`
8. `directives/today_in_ai.md`
9. `memory/workflows/today-in-ai-voice.md`
10. `memory/research/today-in-ai-humor-visual-research.md`
11. `automations/today-in-ai/fireship-thumbnail-audit-2026-07-30.md`
12. `automations/today-in-ai/templates/daily-image-brief.md`
13. `automations/today-in-ai/templates/image-assets.template.json`
14. `today-in-ai/log.md`
15. `.agents/skills/no-ai-slop/SKILL.md`
16. `.agents/skills/no-ai-slop/eval.md`
17. `.agents/skills/social-publisher/SKILL.md`
18. `~/.codex/skills/.system/imagegen/SKILL.md`
19. `.agents/skills/today-in-ai-thumbnail/SKILL.md`
20. `youtube/fireship-today-in-ai-library/00-INDEX.md`
21. `youtube/fireship-today-in-ai-library/02-writing-mechanics.md`
22. `youtube/fireship-today-in-ai-library/03-title-mechanics.md`
23. `youtube/fireship-today-in-ai-library/04-thumbnail-mechanics.md`
24. `youtube/fireship-today-in-ai-library/05-today-in-ai-playbook.md`

Use the July 23, 2026 edition and its platform manifests only as structural references. Do not reuse its stories, jokes, or Unicode-bold formatting.

The historical comparison is intentionally bounded. Review only the seven calendar days before the current run. Do not scan the full archive.

# STEP BY STEP

Follow `directives/today_in_ai.md` from preflight through logging.

1. Determine the current date in `America/New_York`.
2. Run `python3 execution/today_in_ai_novelty.py --date <YYYY-MM-DD> --write`.
3. Read `today-in-ai/editions/<YYYY-MM-DD>/recent-seven-review.md` and open every listed final image. This is a maximum of seven prior editions.
4. Read the last successful log entry and research since that run first, with a 36-hour maximum normal lookback. Freshness is an eligibility rule, not a substitute for importance. This briefing must publish every calendar day. If no accurate, previously uncovered candidate clears the normal significance bar, expand the search deliberately up to seven calendar days and choose the strongest verified AI story that has not been covered. Never use a story older than seven days. A slow news day is not a no-publish condition.
5. Run the Postiz and account-routing preflight for LinkedIn and X. Do not open or preflight YouTube, and do not require browser control for publishing.
6. Use `.agents/skills/x-youtube-research/SKILL.md` to scan X first. Check the current official AI company, product, lab, researcher, and founder accounts plus major AI reporting accounts for candidate announcements since the previous successful run. Save the direct X status URLs. Then run a broad front-page sweep across official AI newsrooms and independent AI desks such as Reuters Technology/AI, AP, TechCrunch AI, The Verge AI, Ars Technica AI, and other credible current sources. Review at least twelve current leads across the combined source surfaces, or document that fewer existed after every required surface was checked. Then open the official release, documentation, paper, court filing, policy text, repository, or incident report behind each candidate.
7. Verify the Gmail connector profile is `hi@paytonbilodeau.com`. Search every current AI newsletter in the mailbox, not only a fixed allowlist. Start with the confirmed recurring editorial sources: TLDR AI, The AI Brief, The Neuron, The Rundown AI, Superhuman, The AI Daily Brief, There's An AI For That, AI with Remy, Ben's Bites, Marcus on AI, and Morning Brew's AI coverage. Confirmed sender addresses include `dan@tldrnewsletter.com`, `ai-information@mail.beehiiv.com`, `theneuron@newsletter.theneurondaily.com`, `news@daily.therundown.ai`, `superhuman@mail.joinsuperhuman.ai`, `aidailybrief@mail.beehiiv.com`, `hi@mail.theresanaiforthat.com`, `remy@mail.aiwithremy.com`, `bensbites@substack.com`, `garymarcus@substack.com`, and `crew@morningbrew.com`. Then run a broad mailbox sweep across current Updates, Promotions, and other inbox categories for recurring AI briefings, digests, roundups, Substacks, and product or research newsletters that are not yet on the list. Include newly discovered relevant senders in the day's newsletter desk and record them in `sources.md`; do not wait for the standing prompt to be manually updated. Separate editorial newsletters from company or product emails so self-interested claims receive the correct evidence label. Record the matching message count and subjects, then read every current relevant edition in full, not only its subject or snippet. For each, extract the stories selected, ordering, useful source links, plain-language mechanism, concrete examples, caveats, and any framing that helps explain the event. Record those notes in `sources.md` and use cross-newsletter overlap as a strong salience signal while still applying the weighted candidate score. Newsletter reporting and synthesis may be reused as research, but rewrite it in Today in AI's voice, do not copy distinctive wording or jokes, and verify every material claim with the best primary source plus an independent check when needed. If Gmail is unavailable, routed to another account, or has no current editions, record the exact reason for the public-web fallback and inspect the publishers' public editions when available.
8. Verify every material claim with the best available primary source. Label company-reported results, independently check them when possible, and separate current capability from previews, tests, allegations, and projections.
9. Build a scored candidate slate in `sources.md` before choosing the edition. Score every verified candidate from 0 to 4 for audience breadth and consequence, capability/policy/economic/scientific step-change, immediate availability, evidence strength, cross-source salience, and novelty. Weight breadth and step-change three times, availability and evidence twice, and salience and novelty once. Apply the penalties in `directives/today_in_ai.md`. The highest consequential verified story must lead. A niche product feature, badge, interface tweak, funding item, benchmark, or executive story cannot outrank a major model release, broadly available capability, major scientific result, large safety event, or consequential government or court action merely because it is newer or easier to package. If the lead is not the highest-scoring eligible candidate, record the specific evidence-based disqualification in `sources.md`; otherwise the editorial gate fails. Use one story when one event dominates, when the news cycle is slow, or when only one candidate passes. Use two when two consequential events or one useful theme deserves the space, and three when three independent events clear the bar. Use four only on an exceptional day. Default to one or two, but never reduce a passing edition below one previously uncovered story. Cut repetitive or unverifiable items. A company or topic from the rolling window is allowed only after a meaningful new event, and the copy must state exactly what changed. Before writing, ask: `Would a well-informed AI reader say this edition skipped today's obvious biggest story?` If yes, research and rank again.
10. Write from the verified source notes using the mechanisms in `youtube/fireship-today-in-ai-library/02-writing-mechanics.md`, never Fireship's wording, catchphrases, nicknames, exact analogies, jokes, or persona. State the event immediately, expose the contradiction, explain the mechanism in plain language, keep the limitation beside the claim, and end on the concrete consequence or next observable event. Push the humor closer to Fireship when the facts support it: prefer one strong situational premise per story, and allow a sharper punchline, absurd comparison, escalating list, understatement, or one callback instead of sanding every joke into a polite aside. A normal edition may contain two to four funny lines. Humor may be bold, but it cannot change a fact, invent a motive, copy a source, target a victim or identity, or make light of illness, death, layoffs, personal harm, or a serious safety event. Read the edition with the jokes removed and confirm the reporting still works. Run the readability and no-AI-slop gates. Delete announced-importance phrasing and cliché endings including `only time will tell`, `welcome to the future`, `we're just getting started`, `one thing is clear`, and detached joke kickers. Keep all research citations and source URLs in `sources.md`. `copy.txt` is public copy and must contain no URL, `Sources:` footer, citation list, or source link.
11. Run `python3 execution/fireship_reference_scrape.py --max-age-days 3`. Read `youtube/fireship-today-in-ai-library/04-thumbnail-mechanics.md` and open both current contact sheets. Then complete `automations/today-in-ai/templates/daily-image-brief.md`. Use a real recognizable established meme or directly relevant public-figure asset when its premise fits. Do not ask an image model to make a generic substitute. Choose `reference_generation` when an expression, face, costume, prop, or logo must become part of one coherent visual. Choose `cutout_composite` when the exact source must remain unchanged, remove its background, and match light, shadow, edge color, grain, perspective, and occlusion. If no sourced subject fits, use an official press, licensed, public-domain, or owned asset before a clearly justified generated original.
12. Save sourced visuals and current official logos under `today-in-ai/images/<YYYY-MM-DD>/assets/`. Build the schema-version-2 `today-in-ai/editions/<YYYY-MM-DD>/image-assets.json` from the template with source URLs, local paths, hashes, usage notes, production route, composition fields, exact AI Mentorship palette values, heavy typography, locked publication-mark geometry, and official logo sources.
13. Use the built-in image generator to build one coherent 1920 by 1080 visual from the supplied meme, public-figure, press, and official-logo references. Use only Jet Black `#0B0F0D`, Old Money Green `#0F583D`, Mint Green `#72DFA5`, Warm Paper `#F7F8F4`, and White `#FFFFFF` for the designed frame. Natural source colors and exact official logo colors may remain unchanged. Do not invent or approximate a logo. Use semantic logo placement that explains who caused, owns, broke, beat, copied, or benefits from the event. If a generated logo is not exact, repair it with the official asset and rebuild its perspective, lighting, texture, reflection, grain, edge softness, and occlusion. Inspect the intended object surface at full size. Every visible logo pixel must remain inside that surface's usable face and follow its plane without crossing a bevel, seam, gap, or neighboring object. For a keyboard key, the complete mark must sit inside the keycap's top face and stop before its bevel and surrounding gaps. If that cannot be done legibly, change the composition or regenerate. Add exact two-to-five-word headline type after the base visual is approved. Leave the bottom-left badge zone empty.
14. Apply the exact transparent Today in AI master with `python3 execution/today_in_ai_badge.py --input <approved-base-image> --output <final-image>`. The badge must be exactly 230 pixels wide, 84 pixels from the left, and 84 pixels from the bottom, with no backing plate.
15. Run `python3 execution/today_in_ai_assets.py --manifest today-in-ai/editions/<YYYY-MM-DD>/image-assets.json --prompt today-in-ai/editions/<YYYY-MM-DD>/image-prompt.txt`.
16. Rerun `python3 execution/today_in_ai_novelty.py --date <YYYY-MM-DD> --write --check`. If it fails, revise the copy or image and run it again. A failed novelty check blocks publishing.
17. Record the final editorial and visual comparison judgment in `recent-seven-review.md` and `package.md`.
18. Run `python3 execution/today_in_ai_prepare.py --date <YYYY-MM-DD> --dry-run`. Inspect the result and fix every failure.
19. Run `python3 execution/today_in_ai_prepare.py --date <YYYY-MM-DD>` to enforce all local gates, create the manifests, and copy the package to the Desktop delivery folder.
20. Validate and render both payloads locally.
21. Submit LinkedIn and X separately through `execution/social_publisher.py` and Postiz using `--mode now`, `--confirm-upload`, and `--confirm-publish PUBLISH`. Never resubmit a destination already verified for the current date.
22. Verify both Postiz posts, the attached image, and each receipt. Do not retry a possibly successful submission until the existing receipt and Postiz state are checked.
23. Write `today-in-ai/editions/<YYYY-MM-DD>/publish-results.json` with verified `linkedin` and `x` platform records. Never mark the overall status `published` until both destinations are verified.
24. Append the complete result to `today-in-ai/log.md`, including the rolling novelty review result, asset provenance, and both live URLs.
25. Copy the updated `package.md` and `publish-results.json` into the dated Desktop delivery folder and verify their hashes match the workspace files.
26. Only after LinkedIn and X are both verified, run `python3 execution/today_in_ai_retention.py --date <YYYY-MM-DD> --apply`. The script does nothing unless 14 days have passed since the last cleanup. When due, it moves only dated Desktop delivery copies older than the rolling seven-day window to macOS Trash.

# TOOL ACCESS AND WORKAROUNDS

Use `execution/social_publisher.py` and Postiz aliases `linkedin` and `x` for those two publishing actions. If Postiz or either account is unavailable, do not switch routes. Preserve the package, write a failed-run entry with the exact repair step, and stop.

Never use browser automation or direct LinkedIn or X posting to create the posts. The daily publishing route is Postiz only.

Never load or copy secrets from the workspace.

# FORMAT REQUIREMENTS

Use the same exact link-free copy and image on LinkedIn and X. Research links and citations belong only in `sources.md`; public copy must not contain URLs, a `Sources:` footer, a citation list, or source links.

Use normal platform text with no Markdown bold and no Unicode lookalike bold. Put `Today in AI: <Month Day>` on the first line. Put a full blank line after the title, after every heading, and after every sentence or short thought. Every story heading is in title case on its own line with a colon at the end. No two non-empty source lines may touch.

Use one to three stories according to the evidence. Four is exceptional. The full edition is normally 160 to 360 words and never exceeds 450.

Daily publication is a hard rule. Start with the normal 36-hour window, then expand only as needed up to seven calendar days to find at least one accurate, relevant, previously uncovered AI story. Never reach beyond seven days or recycle a covered story merely to fill space. Only a failed accuracy, source, novelty, asset, account-routing, publishing, or verification gate may prevent publication.

# EXAMPLE OF GOOD OUTPUT

```text
Today in AI: July 24

OpenAI Built a Phone Worker:

<First complete sentence.>

<Second complete sentence.>

AI Stole the Answer Key:

<First complete sentence.>

<Second complete sentence.>
```

# WHAT TO AVOID

Avoid unsupported claims, jargon without a short explanation, timid filler jokes, forced jokes, fake urgency, fake-profound endings, copied creator or newsletter phrasing, em dashes, hashtags, emojis, engagement bait, Markdown styling, Unicode lookalike styling, collapsed paragraph spacing, browser-created LinkedIn or X posts, and duplicate submissions on any destination.

Also avoid repeating any story angle, heading, analogy, joke structure, image hook, meme family, subject pose, main composition, prop setup, or visual joke found in the rolling seven-day review.

Do not use an AI-generated generic person in place of a recognizable established meme or directly relevant public figure. Do not use a raw rectangular meme screenshot, white-halo cutout, sticker-like logo, floating logo row, or thin headline type. Never ask the image model to render the Today in AI badge. Never ask it to invent or approximate a company or product logo from text; supply the exact current official asset as a reference.

# SUCCESS CRITERIA

- At least one previously uncovered verified story every calendar day, using the seven-day fallback only when the normal 36-hour window is empty
- One to three verified stories chosen by consequence, with four only on an exceptional day
- Complete edition between 160 and 450 words
- Readability target met when practical
- No-AI-slop evaluation passes
- Public `copy.txt` is link-free, has no `Sources:` footer or citation list, and keeps research URLs only in `sources.md`
- Rolling seven-day novelty check passes
- Every prior image in the bounded review was visually inspected
- No repeated story angle, hook, meme family, main composition, subject pose, or visual joke
- Stories read as cohesive explanations, not stacked source notes or repeated formulae
- Every current relevant newsletter was read in full and its story choices, source links, explanation, and limitations were captured in `sources.md`
- The opening sentence of every story states the event, then connects contradiction to mechanism to consequence
- Humor is Fireship-paced and may be bold when the verified situation supports it, while remaining independent of the factual claim and respectful around real harm
- No Fireship wording, catchphrase, nickname, exact analogy, or composition is copied
- No announced-importance phrasing such as `this matters` or `that matters`
- No cliché or branded ending
- Every title, heading, sentence, and short thought is separated by a full blank line in `copy.txt`
- Final image is exactly 1920 by 1080 and passes logo QA
- `image-assets.json` schema version 2 passes and records source URLs, local hashes, usage notes, production route, composition fields, the exact AI Mentorship palette, heavy type, locked badge geometry, and official logo sources
- Known memes and public figures use recognizable sourced assets rather than generic generated substitutes
- Reference-aware generation or a professionally integrated background-removed cutout was used
- Every company or product logo is an exact sourced reference and passes fidelity and material-integration QA
- Every in-scene logo is fully contained by its intended object's usable surface and does not cross an unplanned bevel, seam, gap, or object boundary
- The transparent Today in AI badge is exactly 230 pixels wide and 84 pixels from the left and bottom
- LinkedIn and X each return a Postiz receipt and a verified published result
- Complete package exists in the dated workspace and Desktop folders
- The package contains `recent-seven-review.md`
- `publish-results.json` reports `published` only after LinkedIn and X are verified
- `today-in-ai/log.md` contains the full run record
- The post-publication retention check ran and reported whether cleanup was due

# OUTPUT DESTINATION

Save the edition, sources, rolling seven-day review, image prompt, image asset manifest, sourced assets, image, manifests, and results in the dated workspace folders. Copy the complete package to `~/Desktop/Today in AI/Today in AI - <YYYY-MM-DD>/`.

Keep the canonical workspace editions, images, logs, manifests, results, and receipts. The biweekly cleanup applies only to dated Desktop delivery copies and uses macOS Trash so recovery remains possible.

# HUMAN REVIEW

The scheduled run or Payton's current-day manual request is the publishing authorization for LinkedIn and X. Do not ask for a second confirmation. Publish when every gate passes. If a required gate fails before external publishing begins, publish nothing. If one destination fails after the other is verified, preserve the successful result, log the partial distribution and exact repair step, and never retry without checking receipts and live platform state.
