# Prepare one current Today in AI edition

Use this packet with your completed [run template](RUN-TEMPLATE.md) and the
[directive](../directives/today_in_ai.md). The public template defaults to drafts.
An actual publication needs your own explicit destination authority.

## Establish the run

Determine the current date in the configured timezone. Inspect the existing
edition package, destination receipts and provider jobs before working. Resume
a partial run; never replay missed dates or resubmit a queued or verified post.
Use your own private research inbox and brand assets.

Run `python3 scripts/today_in_ai_novelty.py --date YYYY-MM-DD --write` from
your configured workspace. Read the bounded seven-day review and inspect its
listed images. Compare story angles, hooks, joke structures and compositions.

## Research and choose the lead

Start since the last successful edition, normally within 36 hours. Investigate
official announcements and researcher posts, then broader reporting and relevant
newsletters. If inbox access is unavailable, record the failure and use public
editions where possible. Newsletters help discover and explain stories; verify
technical and factual claims against the original documentation, paper, release,
filing or experiment. Keep source publication dates separate from event dates.

Review at least twelve current leads, or document the smaller set found after
checking all required surfaces. Score verified candidates from zero to four for
audience consequence, step-change, availability, evidence, salience and novelty.
Weight those factors 3, 3, 2, 2, 1 and 1 respectively. Record the score and any
evidence-based disqualification. The most consequential eligible story leads.
Ask whether the edition missed the day's obvious major event.

Use one or two stories normally, three when each earns its space, and four only
on an exceptional day. A slow day permits a deliberate search up to seven days,
never a recycled angle or an older story. Keep vendor claims attributed and
distinguish shipped capability, previews, allegations and projections.

## Write and check

Write 160 to 450 words for a curious, nontechnical reader. Explain the event,
mechanism, limitation and concrete consequence in complete connected sentences.
Use original situational humor when the verified facts support it. Check the
literal reading of every joke; do not invent a motive, result or experience.

Start `Today in AI: <Month Day>`. Use title-case story headings ending in colons.
Leave a blank line between every nonempty line. Use ordinary platform text,
without Markdown bold or Unicode imitation bold. Each story needs at least two
spaced body paragraphs. The validator budgets one story at 150 to 360 words;
two at 90 to 210 and 60 to 180; three at 70 to 170 then 45 to 130 each;
four at 65 to 150 then 35 to 105 each. Keep the complete edition within the
overall 160-to-450-word range. Keep all URLs and citations
in `sources.md`; the full public `copy.txt` is link-free.

## Generate the image as a complete scene

Fill [the image brief](../templates/daily-image-brief.md) and
[schema 3](../templates/image-assets.template.json). Retain authorized source
images, current official logo references, source URLs, rights notes and hashes.
Use a recognizable reference only when its identity explains the story. Authentic
screenshots and brand source files stay unchanged.

Generate a complete 1920 by 1080 scene with the exact two-to-five-word headline
and every required mark together. Use the supplied reference images. Preserve
exact recognizable logo structure. Render every logo in the same image style.
Integrate the Today in AI mark into the scene. No flat logo overlays. Preserve
structure, spelling, proportions, spacing and negative space while matching the
scene's material, linework, texture, light and perspective. The publication mark
appears once on a meaningful surface. Correct defects by native editing or
regeneration and inspect full-size and phone-size results.

Use the example palette #0B0F0D, #0F583D, #72DFA5, #F7F8F4 and #FFFFFF in this
validator. If you choose another palette or publication mark, update your local
validator and template together. The generator's final prompt must include these
colors, the exact headline and the schema's required reference constraints.
The legacy badge script is for inspecting historical packages, not new images.

## Package locally

Save `copy.txt`, `sources.md`, `image-prompt.txt`, `image-assets.json`, the final
image and `package.md` under the dated edition directory. The source pack needs
the candidate slate, at least three distinct HTTPS source URLs, material claim
checks and voice review.

Run the asset validator, rerun novelty with `--write --check`, then run
`python3 scripts/today_in_ai_prepare.py --date YYYY-MM-DD --dry-run`. Resolve
every failure before the packaging command without `--dry-run`. Configure the
workspace and delivery arguments for your own folders. Validate and render both
destination manifests locally. Rendering does not upload or publish.

## Authorized publication and recovery

Before a live action, verify the intended X and LinkedIn integration identities.
Run `python3 scripts/social_publisher.py doctor --online` and require
`postiz_authenticated` and `postiz_today_in_ai_ready`. Generic `local_ready`
does not prove account readiness. Verify live integration routing separately.

Use Postiz for X and LinkedIn. Submit X first as one complete post with the image.
The manifest must contain `publication: today-in-ai` and `thread_policy: single`.
Inspect the rendered payload: exactly one X post and one value containing all
copy and the image. Never split the edition into a thread. Verify the account's
long-post capability before using copy beyond its supported limit.

Wait for the original X publishing record to reach terminal `PUBLISHED` before
submitting LinkedIn. A create response or `QUEUE` is not publication. Record the
Postiz post ID, release ID, public URL and an independent destination check for
each platform. The adapter records provider acceptance; the run owner performs
the terminal and live checks. Mark the overall edition published only when both
destinations are independently verified.

The adapter writes a private submission journal before upload. If an action is
uncertain, inspect that journal and the original provider job before retrying.
An existing journal blocks even a forced resubmission. Never recreate a queued
or verified destination. Preserve successful destinations while repairing only
missing ones. This portable template has no browser-posting fallback; a creator's
private recovery authorization is not transferable to its readers.

Save copy, asset hashes, destination evidence, exact states and the next action.
After both destinations are verified, preserve the compact research and publication
record. Optional cleanup requires a separately authorized exact-file plan with
verified retained copies, hashes and restore paths. Follow [the retention guide](../docs/retention.md).
The legacy retention command now reports retirement and moves nothing. Report partial publication accurately.
