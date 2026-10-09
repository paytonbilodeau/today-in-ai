# Today in AI

[![Repository quality](https://github.com/paytonbilodeau/today-in-ai/actions/workflows/quality.yml/badge.svg)](https://github.com/paytonbilodeau/today-in-ai/actions/workflows/quality.yml)

An automated daily AI news brief that researches, verifies, writes, illustrates, and publishes itself to my LinkedIn and X every morning.

Live output, every day:

- LinkedIn: [linkedin.com/in/paytonbilodeau](https://www.linkedin.com/in/paytonbilodeau)
- X: [x.com/paytonbilodeau](https://x.com/paytonbilodeau)

## What it looks like

Every edition is one link-free post and one original 1920 by 1080 image, identical on both platforms. This is the August 27, 2026 edition, researched, written, illustrated, published, and verified by the system:

![August 27, 2026 edition image](assets/example-edition.png)

> Nvidia's $96 Billion Quarter:
>
> Nvidia made $96.2 billion in three months, more than double its revenue from the same quarter last year.
>
> [...]
>
> The AI gold rush has found the hardware store, and it is ordering by the million.
>
> [...]
>
> AI is no longer only a software story.
>
> It is becoming one of the largest physical construction and equipment cycles in technology history.

## What a daily run does

1. Reviews its own last seven editions so it never repeats a story angle, heading, joke structure, meme family, or image composition. A deterministic novelty check blocks publishing if it does.
2. Researches across three surfaces: official AI company and researcher accounts on X, major newsrooms and AI desks, and a full read of every AI newsletter in a dedicated inbox (TLDR AI, The Neuron, The Rundown, The AI Daily Brief, Ben's Bites, and any new sender it discovers).
3. Verifies every material claim against the best primary source. Company-reported numbers get labeled as company-reported. Previews and projections never read as shipped capability.
4. Scores every verified candidate on a weighted rubric: audience consequence and capability step-change at 3x, availability and evidence strength at 2x, salience and novelty at 1x. The biggest verified story must lead, and the run has to answer one question before writing: would a well-informed reader say this edition skipped the day's obvious biggest story?
5. Writes a 160 to 450 word edition in plain language for smart, non-technical adults. Event first, then the contradiction, the mechanism, the limitation, and the concrete consequence. Humor is allowed to be bold but can never change a fact.
6. Builds one original 16:9 image from sourced assets: real memes, real public figures, current official logos supplied as structural references, then renders every mark and the exact headline with the scene in the same image style.
7. Submits X first as one complete post, waits for terminal PUBLISHED, then submits LinkedIn through Postiz. It verifies both destinations independently and records separate receipts.

A run publishes only after every gate passes: accuracy, novelty, readability, an anti-AI-slop pass on the writing, image and logo QA, and account routing. A failed prepublication gate blocks submission. If a destination fails after another succeeds, the run preserves the successful post and reports partial publication with the exact repair step.

## How it runs

The whole system is instructions plus small deterministic scripts. A scheduled agent task (Codex in the ChatGPT desktop app) reads the production packet in `prompts/`, follows the standing rules in `directives/`, and calls the Python scripts in `scripts/` for the parts that must never be left to model judgment: novelty checking, asset validation, pre-publish gating, submission journals, and a fail-closed legacy retention entry point.

That split is the design opinion this repo demonstrates: the model does research, judgment, and writing; deterministic code does verification, packaging, and publishing. Trust lives in the gates, not in the model's confidence.

## Repo layout

- `prompts/` — the production packet the scheduled agent runs from, plus the prompt used to update the standing task
- `directives/` — the standing editorial, image, and publishing rules (the system's constitution)
- `scripts/` — the deterministic Python: novelty check, schema-3 asset validator, historical badge tool, pre-publish gate, Postiz publisher, retired age-only cleanup entry point, and the reference scraper for studying pacing
- `context/` — accumulated context the run reads before working
- `templates/` — the daily image brief and the image asset manifest schema
- `docs/` — the process decomposition, the automation decision record, the maintenance plan, and the iteration log of every change to the system with the reason for it

## Make it yours

The system is templated so you can run your own daily brief:

1. **Workspace.** Scripts and prompts assume `~/workspace` as the working folder. Change the `WORKSPACE` constant at the top of each script, or point a symlink at your own folder.
2. **Research inbox.** Configure your own authorized AI-newsletter research inbox in the private run template. Discover relevant current senders rather than treating a list as complete.
3. **Publishing.** Create your own Postiz account and `linkedin` / `x` integration aliases. Keep credentials outside the repo, the way `docs/tool-access-plan.md` describes.
4. **Brand.** The palette, badge, and voice are mine. Supply your official mark as a structural reference and write your own voice guide. Update the asset validator and schema together when changing the palette or mark.
5. **Trigger.** Any scheduled agent that can read files and run scripts works. Mine is a daily Codex task in the ChatGPT desktop app that reads `prompts/today-in-ai-automation-prompt.md` and follows it end to end.

## What's not here

This is a cleaned copy of the production system. Credentials live outside the repo in owner-only files under my home directory, loaded by path at runtime. No API keys, tokens, or account credentials exist anywhere in this repo, and the prompts explicitly forbid the agent from loading secrets out of the workspace. Your voice guides, source notes and issue archives belong in your own private workspace. The current public run packet links to portable files in this repository.

## How it was built

I direct AI to build software. This system was built by describing what a trustworthy daily brief has to do, then iterating with Claude Code and Codex until every failure mode had a gate: duplicate posts, unverified claims, recycled jokes, broken logos, silent partial publishes. The iteration log in `docs/` records every one of those changes and why it was made.


## Current template

Version 1.1.0 defaults to drafts until you authorize your own destinations. Start
with [the run template](prompts/RUN-TEMPLATE.md). Run the 31 local checks with
`python3 -m unittest discover -s tests -v`. Schema 1/2 and badge support are
retained for historical inspection; new generated scenes use schema 3.
