# Cleanup follows verified completion

Preserve partial editions and any research, asset or delivery work needed for a
retry. A folder's date does not establish that its contents are safe to remove.
The legacy `today_in_ai_retention.py` command now reports retirement, including
when called with `--apply`, and changes neither files nor its old state file.
It does not implement a replacement mover.

After both publication destinations are independently verified, save the final
copy, publication evidence, asset identities and useful examples. If cleanup is
authorized, prepare an exact-file plan with a completion time, due time, source
path, retained copy, size, hash and recoverable destination for each file. A
24-hour delay is a useful starting policy; choose it explicitly for your setup.

Before moving anything, verify the retained bytes and recheck that the source is
not shared by an unfinished edition. Review the exact plan, use a recoverable
Trash move through your chosen tool, and verify the destination bytes afterward.
Keep a restore map and distinguish a Trash move from reclaimed disk space. Do
not empty Trash as part of this workflow. Keep private paths and state out of
public repositories. A scheduler entry or successful command is not recovery proof.
