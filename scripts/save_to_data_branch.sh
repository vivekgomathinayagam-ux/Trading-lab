#!/usr/bin/env bash
# Copy files into the "data" branch and push, safely alongside other writers
# (the Railway bot pushes snapshots there every 15-60 minutes, and other labs).
# Each attempt starts from the newest data branch, so a race never needs a rebase.
#
#   scripts/save_to_data_branch.sh "commit message" SRC1:DEST1 [SRC2:DEST2 ...]
#   SRC is a directory (its files are copied) or a glob; DEST is a path in the data branch.
set -euo pipefail
msg="$1"; shift
git config user.name "compound-city-lab"
git config user.email "lab@users.noreply.github.com"
root="$(pwd)"
for attempt in 1 2 3 4 5 6; do
  git fetch origin data --depth=1 || true
  rm -rf ../databranch && git worktree prune
  if git rev-parse --verify -q origin/data >/dev/null; then
    git worktree add -f -B data ../databranch origin/data
  else
    git worktree add -f --orphan -b data ../databranch
  fi
  for pair in "$@"; do
    src="${pair%%:*}"; dest="${pair#*:}"
    mkdir -p "../databranch/$dest"
    if [ -d "$root/$src" ]; then cp -r "$root/$src"/. "../databranch/$dest/"; else cp $root/$src "../databranch/$dest/"; fi
    (cd ../databranch && git add "$dest")
  done
  cd ../databranch
  if git diff --cached --quiet; then echo "no changes"; exit 0; fi
  git commit -q -m "$msg"
  if git push origin HEAD:data; then echo "saved on attempt $attempt"; exit 0; fi
  cd "$root"
  sleep $((attempt * 7))
done
echo "could not push to data after 6 attempts" >&2
exit 1
