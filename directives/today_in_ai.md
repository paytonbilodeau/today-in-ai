# Today in AI

Updated: August 26, 2026

## Purpose

Publish one short, funny, plain-language, fact-checked AI briefing with one 16:9 image to Payton's LinkedIn and X through Postiz each day. YouTube is not a Today in AI publishing destination.

Voice and editorial rules: `memory/workflows/today-in-ai-voice.md`

Humor and visual research: `memory/research/today-in-ai-humor-visual-research.md`

Current thumbnail audit: `automations/today-in-ai/fireship-thumbnail-audit-2026-07-30.md`

Current Fireship corpus and Today in AI playbook: `youtube/fireship-today-in-ai-library/00-INDEX.md`

Edition log: `today-in-ai/log.md`

Visual logo: `today-in-ai/brand/selected/today-in-ai-logo-white-transparent.png`

Personal social publishing control layer: `execution/social_publisher.py`

## Approval State

Once created, the standalone Today in AI scheduled task in Codex in the ChatGPT desktop app authorizes the complete workflow on each scheduled run. A manual request for today's Today in AI post provides the same authorization. Both triggers include immediate LinkedIn and X publishing through Postiz after every required gate passes.

Do not ask for a second publishing confirmation after either trigger. Never interpret a request for a mock, review, draft, preview, or image by itself as permission to post.

## Current Access State

As of August 15, 2026:

- The Gmail connector is verified as `hi@paytonbilodeau.com`. This is the Today in AI newsletter-discovery inbox.
- Payton subscribed that address to AI newsletters beginning August 5. Current recurring editorial sources include TLDR AI, The AI Brief, The Rundown AI, The Neuron, Superhuman, There's An AI For That, The AI Daily Brief, Morning Brew's AI coverage, Ben's Bites, Marcus on AI, and AI with Remy. AI with Remy is verified in the inbox at `remy@mail.aiwithremy.com`. The list is a starting registry, not a closed allowlist.
- TLDR AI's current message requests signup confirmation. Treat its subscription as pending until regular editions appear.
- Use the connected Gmail app for Today in AI intake. Do not depend on the workspace multi-account Gmail script.
- Keep `hi@paytonbilodeau.com` connected for Today in AI newsletter discovery. Today in AI depends on no other inbox for its newsletter intake.
- Postiz authentication and Payton's LinkedIn and X integration aliases exist. Recheck them before posting and after any failure.

Never place Gmail or Postiz credentials in the workspace.

## Research Window

Normal news search window: since the previous successful run, with a 36-hour maximum lookback.

Daily publication floor: publish at least one accurate, relevant, previously uncovered AI story every calendar day. If the normal window has no candidate that clears the significance bar, expand the search deliberately up to seven calendar days and choose the strongest verified unused story. Never use a story older than seven days. Significance ranks the field; it does not permit a zero-story edition.

Novelty comparison window: the seven calendar days before the current edition. Do not scan the full archive. Use `execution/today_in_ai_novelty.py` to surface only those editions.

## 1. Preflight

1. Read `memory/workflows/today-in-ai-voice.md`.
2. Read `memory/research/today-in-ai-humor-visual-research.md`.
3. Run `python3 execution/fireship_reference_scrape.py --max-age-days 3`.
4. Read `youtube/fireship-today-in-ai-library/02-writing-mechanics.md`, `03-title-mechanics.md`, `04-thumbnail-mechanics.md`, and `05-today-in-ai-playbook.md`.
5. Open both contact sheets under `youtube/fireship-today-in-ai-library/data/contact-sheets/`.
6. Read `automations/today-in-ai/fireship-thumbnail-audit-2026-07-30.md`.
7. Read the latest entries in `today-in-ai/log.md`.
8. Confirm the current date and America/New_York timezone.
9. Confirm the `no-ai-slop` skill is present in `.agents/skills/` and `.claude/skills/`.
10. Read `.agents/skills/today-in-ai-thumbnail/SKILL.md`.
11. Build the bounded novelty report:

```bash
python3 execution/today_in_ai_novelty.py --date <YYYY-MM-DD> --write
```

12. Read `today-in-ai/editions/<YYYY-MM-DD>/recent-seven-review.md`.
13. Open every final image listed in that report. Review the actual image, not only its filename or prompt.
14. Confirm Postiz and account routing:

```bash
python3 execution/social_publisher.py doctor --online
npx --yes postiz@2.0.15 integrations:list
```

If Postiz, LinkedIn, or X is unavailable, do not use another posting route. Append a failed-run entry and stop.

## 2. Gather

Use `.agents/skills/x-youtube-research/SKILL.md` and scan X first. Start with the current official accounts for OpenAI, ChatGPT, Anthropic, Claude, Google DeepMind, Gemini, NotebookLM, xAI, Grok, Perplexity, Microsoft AI, and Meta AI, then check directly relevant founders, researchers, repositories, institutions, and major AI reporting accounts. Save direct status URLs for every candidate.

Open the primary source behind each X candidate before ranking it: official newsroom, product page, documentation, release notes, model card, research paper, repository, court filing, policy text, or incident report.

Then use the Gmail connector authenticated as `hi@paytonbilodeau.com` as the team-curated news desk.

Search since the previous run for:

- `dan@tldrnewsletter.com`
- `ai-information@mail.beehiiv.com`
- `news@daily.therundown.ai`
- `theneuron@newsletter.theneurondaily.com`
- `superhuman@mail.joinsuperhuman.ai`
- `hi@mail.theresanaiforthat.com`
- `aidailybrief@mail.beehiiv.com`
- `bensbites@substack.com`
- `crew@morningbrew.com`
- `remy@mail.aiwithremy.com`
- `garymarcus@substack.com`

For Morning Brew, extract AI stories only. Record matching message count and subjects.

After searching the known senders, sweep all current mailbox categories for additional recurring AI briefings, digests, roundups, Substacks, and product or research newsletters. Search broadly enough to catch a new sender whose name or subject is not already in this file. Add every newly discovered relevant sender to the day's `sources.md` newsletter desk without waiting for a manual registry update. Separate editorial newsletters from company and product emails because the latter are primary announcement leads or self-interested claims, not independent checks.

Read every current relevant newsletter in full. Subjects and snippets are not enough. Capture its story selection and ordering, cited or linked sources, plain-language mechanism, concrete examples, useful caveats, and explanatory framing in `sources.md`. Treat these team-researched briefings as secondary research desks: their overlap is a strong signal that a story belongs in the candidate slate, and their explanation can reveal the mechanism or consequence the official announcement buried.

Reuse newsletter reporting and synthesis as research, then rewrite it in the Today in AI voice. Do not copy distinctive sentences, jokes, analogies, or structure. Verify every material claim against the best primary source and use an independent check when a company is grading itself. Newsletter consensus strengthens cross-source salience, but it does not override the weighted consequence score or turn an unverified claim into evidence.

Use newsletter overlap to rank candidates and catch stories the X scan missed. Cross-check the newsletter desk with:

- Current AI company and researcher posts on X
- Official AI company newsrooms
- Current model release notes and documentation
- Broad independent AI desks, including Reuters Technology/AI, AP, TechCrunch AI, The Verge AI, and Ars Technica AI when current and accessible
- Credible independent reporting when a company is grading itself

Review at least twelve current leads across the combined X, newsletter, official-source, and independent-news surfaces. If fewer than twelve exist inside the active window, record every surface checked and the actual count. Do not stop discovery when the first publishable story appears.

If the inbox is unavailable, routed to the wrong account, or contains no current editions:

1. Keep the X and official-source research already completed.
2. Use public editions from those publishers.
3. Mark the run `newsletter_fallback: public_web` and record `connector_unavailable`, `account_mismatch`, or `no_current_messages` as the reason.
4. Do not let the missing inbox block a complete edition.

Build a candidate list with:

- Story
- Discovery sources
- Claimed facts and numbers
- Company or organization
- Primary source
- Independent check, when needed
- Previous-edition overlap
- Rolling seven-day story, angle, heading, analogy, and joke overlap
- Audience breadth and consequence score
- Capability, policy, economic, or scientific step-change score
- Immediate availability score
- Evidence-strength score
- Cross-source salience score
- Novelty score
- Newsletter coverage table: publisher, subject, date, stories selected, ordering, useful source links, mechanism or explanation, limitations, and verification status
- Weighted total and any penalty
- Selection or rejection reason
- Plain-language explanation
- Possible comic premise

## 3. Verify

Newsletter coverage and X discussion are discovery, not final evidence.

Use:

- Official newsroom or product blog
- Official documentation, release notes, or model card
- Official research paper
- Official company or researcher X account
- Government or institutional data
- Independent evidence for performance claims

For each candidate:

1. Write the precise claim.
2. Open the primary source.
3. Confirm names, dates, availability, numbers, prices, regions, model names, and limitations.
4. Label company-reported results.
5. Separate what works now from what is promised, previewed, tested, or projected.
6. Apply the Cal Newport checklist in the voice guide.
7. Cut an unverifiable claim.
8. If a joke changes the reader's understanding of the fact, cut the joke.

If credible sources disagree, describe the disagreement or cut the story.

## 4. Rank

Score each verified story from 0 to 4 on:

- Audience breadth and consequence, weighted `x3`
- Capability, policy, economic, or scientific step-change, weighted `x3`
- Immediate availability or current effect, weighted `x2`
- Evidence strength, weighted `x2`
- Cross-source salience, weighted `x1`
- Novelty, weighted `x1`

Apply these penalties:

- `-8` for funding-only news, executive gossip, benchmark-only claims without a real-world consequence, or a repeat without a real update
- `-5` for a minor interface, badge, labeling, or niche workflow change without broad immediate consequences

Write the complete scored slate into `sources.md`. Lead with the highest-scoring eligible story. If another eligible candidate scores higher, the selected lead fails unless `sources.md` records a specific evidence-based disqualification. Freshness breaks close ties; it does not outweigh consequence, breadth, or step-change.

Run a final dominance check before writing: would a well-informed AI reader say the edition skipped the day's obvious biggest verified story? If yes, return to discovery and ranking. A broadly available frontier-model release, major capability change, large scientific result, serious safety event, or consequential government or court action normally outranks a niche product feature.

Choose the story count from the evidence:

- Use one story when one event dominates and supports a complete explanation.
- Use two when two consequential events deserve attention or reveal one useful theme.
- Use three when three independent events clear the evidence and consequence bar.
- Use four only on an exceptional day when the fourth changes what the reader can do or understand.

Default to one or two. One is fully acceptable on a slow day. Do not pad the edition beyond the strongest verified unused story.

### Rolling Seven-Day Editorial Rule

- Do not repeat the same story, angle, heading, analogy, or joke structure from the rolling window.
- A company or topic may return only after a meaningful new event. State exactly what changed instead of recapping the earlier story.
- Prefer a genuinely new story when two candidates are close.
- If the normal 36-hour window has no sufficiently significant story, expand the search up to seven calendar days and publish the strongest accurate, relevant, previously uncovered candidate.
- Never use a story older than seven days or recycle a covered story merely to fill space.
- A slow news day does not fail the novelty gate. Only an actual accuracy, source, novelty, asset, account-routing, publishing, or verification failure can stop publication.

## 5. Write the Factual Draft

Write a humor-free factual draft first.

Required format:

```text
Today in AI: <Month Day>

<Lead Heading, 3 to 7 Words>:

<Lead sentence one>

<Lead sentence two>

<Story 2 Heading, 3 to 7 Words>:

<Story 2 sentence one>

<Story 2 sentence two>

<Story 3 Heading, 3 to 7 Words>:

<Story 3 sentence one>

<Story 3 sentence two>

<Optional Story 4 Heading, 3 to 7 Words>:

<Optional story 4 sentence one>

<Optional story 4 sentence two>
```

Put a full blank line after the title, after every heading, and after every sentence or short thought. No two non-empty source lines may touch.

Keep research evidence and links in `sources.md`. Public `copy.txt` must contain no URL, `Sources:` footer, citation list, or source link. The same exact link-free copy goes to LinkedIn and X.

Adaptive body ranges:

- One story: 150 to 360 words
- Two stories: 90 to 210 for the lead and 60 to 180 for the second
- Three stories: 70 to 170 for the lead and 45 to 130 for each secondary story
- Four stories: 65 to 150 for the lead and 35 to 105 for each secondary story

Normal total length: 160 to 360 words.

Hard cap: 450 words.

Explain unfamiliar terms inline. Remove a number that does not help the reader understand the story.

### Cohesive Story Pass

Each story needs one continuous line of thought:

1. State the event in a concrete sentence.
2. Explain the mechanism in the order a normal reader needs it.
3. Connect the event to a practical consequence.
4. Place the limitation beside the claim it limits.
5. Add humor only after the reader understands the fact.

Do not force every story into the same sentence pattern. Read the whole post aloud as continuous prose. Fix abrupt pivots, press-release phrasing, repeated disclaimer rhythms, stacked facts, and jokes that feel attached after the fact. Concision means removing repetition, not removing the connective reasoning.

Do not announce importance with `this matters`, `that matters`, `why it matters`, `what matters is`, `this is important`, or a close variation. State the practical consequence, affected person, changed capability, or limitation directly.

Use the mechanisms in `youtube/fireship-today-in-ai-library/02-writing-mechanics.md`: event now, contradiction, concrete scope, mechanism, and consequence. Never copy Fireship's wording, nickname, catchphrase, exact analogy, creator persona, or sponsor signoff.

End on the specific capability, limitation, next verified event, or second-order consequence. Ban `only time will tell`, `welcome to the future`, `we're just getting started`, `one thing is clear`, and detached joke kickers.

## 6. Add Humor

Use the humor rules in the voice guide.

1. Find the absurdity already present in the facts.
2. Give each suitable story one strong comic premise instead of a polite aside.
3. Allow a sharper punchline, absurd comparison, escalating list, understatement, or one callback when it grows directly from the verified mechanism.
4. A normal edition may contain two to four funny lines. Do not force an equal joke count across stories.
5. Do not soften a good situational joke merely because it is bold. Restraint is required around victims, illness, death, layoffs, personal harm, identity, private life, politics, and serious safety events.
6. Read the post with the jokes removed and confirm the explanation is still complete.
7. Check that no joke invents a motive, strengthens a claim, copies a source's distinctive line, or targets a victim, identity, appearance, private life, illness, death, layoff, or political group.

Humor should improve recall, explanation, or the pleasure of reading. A bold joke is welcome when it is accurate, immediate, and aimed at the situation, incentive, product behavior, or absurd process. A joke that needs falsehood, cruelty, or a paragraph of setup gets cut.

## 7. Run the No-AI-Slop and Readability Gates

Apply `.agents/skills/no-ai-slop/SKILL.md` and evaluate against `.agents/skills/no-ai-slop/eval.md`.

Claude Code uses the byte-matched `.claude/skills/no-ai-slop/` copy.

Check:

- No throat-clearing
- No binary contrast template
- No fake reveal
- No inflated importance
- No stand-alone importance claim
- No vague attribution
- No robotic rhythm
- No fake-profound ending
- No summary paragraph
- No em dash
- No banned phrase

Calculate word count, character count, and Flesch-Kincaid grade level:

```bash
python3 execution/text_readability.py --json <draft.txt>
```

Target grade: 7 to 9.

Accuracy wins if a necessary name or technical term raises the score.

## 8. Build the Daily Image

Every edition has one image based on the lead.

1. Read `youtube/fireship-today-in-ai-library/04-thumbnail-mechanics.md` and open both current corpus contact sheets.
2. Write a two-to-five-word image hook that does not repeat the full title.
3. Complete `automations/today-in-ai/templates/daily-image-brief.md`, starting with a real, recognizable established meme or directly relevant public-figure asset when its visual premise fits the verified story. Preserve the recognizable crop, pose, expression, and object relationship. Do not replace a known subject with an AI-generated generic person.
4. If no established meme fits, use an official press asset, licensed asset, public-domain asset, owned asset, or a clearly justified generated original in that order. Record why a generated original was necessary.
5. Save every sourced visual and official logo under `today-in-ai/images/<YYYY-MM-DD>/assets/`. Record its source URL, local path, SHA-256, and an accurate usage or rights note. Never imply a license or permission that the source does not provide.
6. Build the schema-version-2 `today-in-ai/editions/<YYYY-MM-DD>/image-assets.json` from `automations/today-in-ai/templates/image-assets.template.json`.
7. Compare the plan with every final image in the rolling seven-day review. Reject any plan that repeats a recent meme family, hook, main composition, subject pose, prop setup, or visual joke.
8. Use Fireship Code Report's high-level packaging grammar: one concrete hook, one recognizable visual transformation, a near-black field, high contrast, semantic logo placement, and a small stable series badge. Do not copy its name, badge, exact layout, red-and-cream treatment, or any specific thumbnail.
9. Use only the AI Mentorship designed palette: Jet Black `#0B0F0D`, Old Money Green `#0F583D`, Mint Green `#72DFA5`, Warm Paper `#F7F8F4`, and White `#FFFFFF`. Natural skin tones, source-meme colors, and exact official logo colors may remain unchanged.
10. Choose `reference_generation` when the joke needs an expression, face edit, costume, transformed prop, or official logo inside the visual premise. Attach the real source subject and current official logos to the built-in image generator. The prompt must say: `Use the supplied reference images for the recognizable subject, meme premise, and official company logos. Preserve the source subject's recognizable identity and the meme's defining pose, expression, crop, and object relationship. Do not invent or approximate any logo. Leave the bottom-left badge area empty. Do not render the Today in AI badge. Use only #0B0F0D, #0F583D, #72DFA5, #F7F8F4, and #FFFFFF for the designed frame.`
11. Choose `cutout_composite` when the exact source image must remain unchanged. Remove the background and match edge color, light direction, shadow, contrast, grain, perspective, and occlusion. Reject raw rectangles, white halos, sticker edges, and floating logos.
12. Use a heavy professional sans-serif for the hook at weight 800 or higher. Prefer Instrument Sans ExtraBold or Black when actually installed. The verified current fallback is `/System/Library/Fonts/Supplemental/Arial Black.ttf`.
13. Add the exact two-to-five-word hook after the base visual is approved. Use no more than three stacked lines, make one word or phrase dominant, and add a dark outline or shadow so it remains readable at 288 by 162 pixels.
14. Use only current official product or company assets from the owner or an authoritative brand source. Supply each mark as a generation reference when it participates in the transformation. Keep the exact shape, proportions, colors, and clear space. If generation changes the mark, replace or edit it with the source asset and rebuild the perspective, lighting, texture, reflections, grain, edge softness, and occlusion. Define the intended physical surface before generation and inspect it at full size afterward. Every visible logo pixel must remain inside that surface's usable face and follow its plane without crossing a bevel, seam, gap, or neighboring object. For a keyboard key, the complete mark must sit inside the keycap's top face and stop before its bevel and surrounding gaps. If the surface cannot hold the exact mark legibly, change the composition or regenerate.
15. Public-figure edits must read as obvious editorial satire. Do not fabricate a criminal act, medical condition, private behavior, or damaging documentary scene.
16. Leave the bottom-left badge zone visually quiet. Apply the exact transparent Today in AI master only with:

```bash
python3 execution/today_in_ai_badge.py \
  --input <approved-base-image> \
  --output <final-image>
```

The badge must be exactly 230 pixels wide, 84 pixels from the left, and 84 pixels from the bottom, with no backing plate.

17. Run the asset gate:

```bash
python3 execution/today_in_ai_assets.py \
  --manifest today-in-ai/editions/<YYYY-MM-DD>/image-assets.json \
  --prompt today-in-ai/editions/<YYYY-MM-DD>/image-prompt.txt
```

18. Export at exactly 1920 by 1080 pixels.
19. Save working files and the final image under `today-in-ai/images/<YYYY-MM-DD>/`.
20. Run the final novelty check:

```bash
python3 execution/today_in_ai_novelty.py --date <YYYY-MM-DD> --write --check
```

21. If the check fails, revise the copy, image plan, or final image and run it again. Do not package or publish a failed candidate.
22. Record the human visual judgment in `recent-seven-review.md` and `package.md`.
23. Copy the complete daily package to `~/Desktop/Leverage/Today in AI/Today in AI - <YYYY-MM-DD>/`.

Image QA:

- Hook is spelled correctly
- Hook reads at phone size
- Hook uses a heavy professional font and remains visually bold at phone size
- Image implication is supported by the post
- Designed colors use the exact AI Mentorship palette
- Human expression supports a calm, rationally optimistic interpretation unless the facts require another emotion
- Logos are official, current, unchanged, supplied as references, and directly relevant
- Logos are integrated into a physical object in the image
- Logos match that object's perspective, lighting, texture, reflections, grain, edge softness, and occlusion
- Every visible logo pixel stays inside the intended object's usable surface and does not cross an unplanned bevel, seam, gap, or object boundary
- A logo assigned to a keyboard key is fully contained inside the keycap's top face and does not spill onto the bevel, key wall, or gaps
- No detached company-logo row or sticker-like company mark
- Meme or visual source asset, source URL, hash, and usage note are documented
- An established meme or public figure uses the recognizable source asset rather than an AI-generated generic substitute
- Reference-aware generation or a professionally integrated background-removed cutout was used
- Meme family, hook, composition, pose, props, and visual joke are new within the rolling seven-day window
- No fake product interface
- No watermark
- Selected Today in AI logo is exact, transparent, 230 pixels wide, and fixed 84 pixels from the left and bottom
- Final dimensions are 1920 by 1080
- Leverage delivery copy matches the workspace final

## 9. Prepare the Platform Package

LinkedIn receives the full link-free edition with blank lines and the image.

X receives the same link-free edition as one long-form post with the image.

Use normal platform text. Do not use Markdown asterisks, Unicode lookalike bold characters, or other fake text styling.

Keep `Today in AI: <Month Day>` on the first line. Put a full blank line after the title, after every story heading, and after every sentence or short thought. Every story heading is in title case on its own line and ends with a colon. Preserve this exact spacing on all platforms.

If Postiz rejects the X long-form post, use a thread. The title and lead go first. Do not silently delete stories.

The daily image means the existing media-post workflow in `execution/social_publisher.py` is used for LinkedIn and X.

First run the safe validation pass:

```bash
python3 execution/today_in_ai_prepare.py --date <YYYY-MM-DD> --dry-run
```

Then run `python3 execution/today_in_ai_prepare.py --date <YYYY-MM-DD>`. It enforces the copy structure, source count, sourced-asset manifest, reference-aware prompt constraints, locked badge geometry, rolling novelty gate, final dimensions, and image hash. It writes the separate manifests and includes `package.md`, `image-assets.json`, and `recent-seven-review.md` in the Desktop package.

## 10. Publish Through Postiz

Publishing is an external action.

Before each live edition:

1. Confirm Postiz authentication and the LinkedIn and X integrations.
2. Build a local media manifest with the exact copy and final image.
3. Render and inspect the Postiz payload locally.
4. Confirm the scheduled run or current-day request provides publishing authorization.

Use the aliases:

- `linkedin`
- `x`

Publish each destination separately so one failure does not hide the other.

Keep a receipt for each result.

Create and submit the LinkedIn and X posts through `execution/social_publisher.py` and Postiz. Never use browser automation or direct LinkedIn or X posting to create them.

## 11. Verify

After submission:

1. Confirm Postiz returned a post ID for each destination.
2. Confirm the result is published, not drafted or scheduled.
3. Confirm the image is attached and renders correctly.
4. Record any partial failure plainly.
5. Do not retry a possibly successful submission without checking the receipt and Postiz state.

## 12. Log

Append one entry to `today-in-ai/log.md` containing:

- Date and run time
- Status: published, partial, failed, or mock
- Newsletter mode: Gmail or public web
- X accounts and direct status URLs used for discovery
- Newsletter message count and subjects
- Covered stories
- Primary source URLs
- Independent source URLs when used
- Exact LinkedIn copy
- Exact X copy
- Image hook
- Workspace image path
- Leverage delivery folder
- Image-generation prompt
- Meme reference URL and adapted visual traits
- Image asset manifest path and source asset hashes
- Source asset usage or rights note
- Official logo asset URLs
- Postiz receipt paths and post IDs
- Rolling review window and novelty result
- Recent images visually inspected
- Candidate meme family and visual differences
- Retention check result and any delivery folders moved to Trash
- Failure and repair step

## 13. Retain Seven Days Of Desktop Delivery Copies

Run this only after LinkedIn and X are both verified as published:

```bash
python3 execution/today_in_ai_retention.py --date <YYYY-MM-DD> --apply
```

The script checks `today-in-ai/retention-state.json`. It acts only when 14 days have passed since the last cleanup. When due, it moves exact `Today in AI - YYYY-MM-DD` directories older than the current seven-day Desktop window to macOS Trash.

Keep the canonical workspace editions, images, logs, manifests, results, and receipts. They are the audit trail and duplicate gate. Never delete them as part of retention.

## Failure Handling

If gathering fails:

- Continue with official primary sources if enough verified news exists.

If verification fails:

- Cut the claim or story.

If writing or humor fails:

- Publish the shorter factual version only if it passes the full editorial gate. Otherwise publish nothing.

If the rolling novelty gate fails:

- Revise the story set, angle, hook, meme family, composition, pose, props, or visual joke.
- Run the deterministic check again.
- If no accurate and relevant candidate can pass, publish nothing and log the exact overlap.

If image generation fails:

- Publish nothing. Today in AI requires the complete copy-and-image package.
- Preserve the verified copy and log the image failure for repair.

If Postiz or either account fails:

- Do not use another posting route.
- Log the exact stage and plain-language error.
- Preserve the package for a safe retry.

## Triggers And Scheduling

The approved automation is the active standalone scheduled task with Codex in the ChatGPT desktop app. It runs every day, including weekends, at 8:00 AM in `America/New_York`, starts a new chat for each run, and uses the local Business Vibe Coding project rather than a worktree.

The shared setup record is `automations/today-in-ai/chatgpt-desktop-setup.md`. The task reads `automations/today-in-ai/today-in-ai-automation-prompt.md` on every run, so workflow changes made from Codex, Claude Code, or the desktop app apply to future runs.

A request such as "do today's Today in AI post," "do the Today in AI post," or a close plain-language variation authorizes the complete workflow for the current date in `America/New_York`:

1. Run every preflight and duplicate check in this directive.
2. Build and visually inspect the rolling seven-day review.
3. Research and verify the current stories.
4. Write the final edition and pass the readability, no-AI-slop, and editorial novelty checks.
5. Create and QA the required image, then pass the visual novelty check.
6. Save the complete workspace and Desktop package.
7. Publish immediately to LinkedIn and X through Postiz.
8. Verify both Postiz results and receipts.
9. Append both results to `today-in-ai/log.md` and `publish-results.json`.
10. Run the post-publication 14-day retention gate only after both destinations are verified.

Do not ask for a second publishing confirmation after a scheduled run starts or Payton gives the daily instruction. Either trigger is explicit publishing authorization for LinkedIn and X. If a required gate fails before external publishing, preserve the work, log the exact failure and repair step, and stop. If a destination fails after the other is verified, keep the successful result, report the partial distribution plainly, and never duplicate it during repair.

### Retired Scheduler

The former launchd scheduler was installed July 23, 2026, hardened July 24, and retired July 25. It remains retired. The approved replacement is the active ChatGPT desktop scheduled task.

- Former label: `com.paytonbilodeau.today-in-ai`
- Installed plist: removed from `/Users/paytonbilodeau/Library/LaunchAgents/`
- Retained source plist: `execution/launchd/com.paytonbilodeau.today-in-ai.plist`
- Retained runner: `execution/today_in_ai_runner.sh`
- Retained production prompt: `automations/today-in-ai/today-in-ai-automation-prompt.md`
- Historical logs: `/Users/paytonbilodeau/Library/Logs/Today in AI/`
- Previous schedules: 8:00 AM primary run and 9:20 AM recovery run

The retained runner exits safely when called without arguments. Its production path requires the explicit `--run-retired` flag. Do not reinstall, bootstrap, or otherwise reactivate launchd unless Payton explicitly asks to replace the ChatGPT desktop scheduled task with the legacy scheduler.
