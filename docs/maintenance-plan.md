# Today in AI Scheduled Task Maintenance

## Normal Checks

- Each scheduled or requested run: confirm the dated `publish-results.json` verifies LinkedIn and X and contains one Postiz receipt for each destination.
- Each scheduled or requested run: return the finished copy, image path, delivery folder, and verified publishing state in the run chat.
- Each scheduled or requested run: require schema-version-2 `image-assets.json`, the asset validator, locked badge compositor, novelty check, and packaging dry-run to pass.
- First three desktop runs after the August 26 update: review the Scheduled inbox and confirm the task started, used the local project, and produced one post on LinkedIn and one on X without opening YouTube.
- Monthly: run `python3 execution/social_publisher.py doctor --online` and validate both Postiz manifests.

## Alert Thresholds

- Any duplicate: pause the active desktop task and audit the verified-result gate. Do not reactivate launchd.
- Any account-routing change: stop publishing until both Postiz aliases are reverified.
- Any logo, palette, or badge-geometry drift: stop publishing until the exact source assets and locked values pass. An in-scene logo that crosses its intended surface boundary, including a keycap bevel or gap, is drift and fails.

## Safe Repair Order

1. Check receipts and Postiz state before any retry.
2. Preserve the dated package.
3. Repair the smallest failed stage.
4. Confirm the finished edition creates exactly one LinkedIn post and one X post with the same copy and image.

## Scheduler Boundary

The approved ChatGPT desktop scheduled task `today-in-ai` is active. The former launchd scheduler remains retired. Do not reload launchd during setup or troubleshooting.
