## Delivery — branch, commit, PR

Only Orchestrator performs git delivery, and only after Verifier has no `FAIL` on the delivered scope and the user explicitly approved the exact action (`WAIT_FOR_APPROVAL`). Present the branch name, file list and commit message first.

Run through the `orchestrator` role of `flowkit_exec.py`. Allowed after approval: `git status` · `git diff` · `git switch -c <branch>` · `git add <explicit paths>` · `git commit -m <message>` · `git push -u origin <branch>` · `gh pr create`.
Never: push to the default branch · force push · `git reset --hard` · `git clean` · `git add -A` · skipping hooks · merging a PR without a separate explicit request. Report the PR link and any step not performed.
