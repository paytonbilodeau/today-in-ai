# Today in AI Automation Decision Record

## Why Automate It

- Frequency: daily
- Manual effort: research, verification, writing, image production, publishing, and receipt logging
- Timing value: strongest when published consistently in the morning
- Repetition: high
- Judgment required: high
- Cost of a bad run: moderate because inaccurate claims or duplicate posts damage trust

## Decision

Run the complete workflow from the standalone Codex scheduled task in the ChatGPT desktop app or when Payton manually asks for that day's post. Keep the strict verification, image, publishing, and duplicate-prevention gates.

The launchd scheduler was retired July 25, 2026 because a daily request gives Payton immediate confirmation that the work ran and removes the laptop uptime and silent-failure risk.

## Expected Return

- Preserves the finished workflow without unattended-run uncertainty
- Gives Payton the post, image, and verified result in the same conversation
- Creates a consistent archive and publishing record
- Produces daily feedback that Payton can use to improve the system

## Main Risks

- Publishing an inaccurate claim
- Repeating a recent story
- Posting without the final image
- Publishing to the wrong account
- Creating duplicate posts after a delayed Postiz response

## Controls

- Primary-source verification
- Rolling seven-day editorial and visual novelty review
- Deterministic duplicate checks for story headings, hooks, meme families, copy similarity, and image hashes
- Structured checks for repeated compositions, poses, prop setups, and visual jokes
- Sourced-image and official-logo hashes with accurate source notes
- Fixed Postiz aliases
- Separate platform submissions and receipts
- Required image QA
- Deterministic result validation after each run
- Recoverable Desktop cleanup every 14 days while preserving the workspace audit history
