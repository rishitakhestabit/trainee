# Bootcamp Day 3 — Git Mastery

## Objective
The goal of Day 3 was to build confidence in handling real-world Git problems such as identifying faulty commits, safely undoing changes, managing parallel work, and resolving conflicts without losing history.

---

## Repository Setup
A Git repository was initialized and developed through a sequence of commits. Changes were made incrementally to simulate a realistic development timeline. One commit intentionally introduced a bug to practice recovery techniques.

---

## Commit Discipline
Each change was committed with a clear message describing the intent. This helped maintain a readable history and made debugging and rollback operations predictable.

---

## Bug Identification Using Git Bisect
When an issue was detected, `git bisect` was used to locate the exact commit where the bug was introduced. This involved marking known good and bad commits and allowing Git to perform a binary search across the commit history.

Commands used:
```bash
git bisect start
git bisect bad
git bisect good 8643c173b924ec4f429c26ef2443b33fef8875e7
git bisect reset
```
This process identified the faulty commit efficiently without manually checking each change.
Fixing Without Rewriting History

After identifying the faulty commit, the bug was fixed using git revert. This approach was chosen to preserve commit history rather than rewriting it with reset or rebase.

Command used:

git revert <faulty-commit-hash>

This created a new commit that safely negated the changes introduced by the bug.
Stash-Based Workflow

To simulate context switching, uncommitted changes were temporarily stored using Git stash. This allowed switching branches or pulling updates without losing local work.

Commands used:

git stash
git pull
git stash apply

This demonstrated how stash helps manage work-in-progress changes in collaborative environments.
Merge Conflict Handling

Two parallel versions of the repository were modified to introduce conflicts in the same file. A merge was attempted, resulting in a conflict which was resolved manually.

The resolution ensured that changes from both sides were preserved correctly before completing the merge.
