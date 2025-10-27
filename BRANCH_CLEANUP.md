Branch cleanup — 2025-10-27
===========================

This file documents branch housekeeping performed on 2025-10-27.

Summary
-------

- Deleted remote branches (from `origin`) and the corresponding local branches:
  - `fix/profile-role-display-2025-10-27` (commit: `1fb5f34`)
  - `postgres-2fa-e2e` (commit: `c7888f2`)

Reason
------

These branches were removed as part of routine repository cleanup. The
deletions were performed from the local clone on 2025-10-27 and pushed to
`origin` to remove the remote references as well.

Recovery
--------

If either branch was deleted prematurely, they can be restored from the
commit SHAs above. To recreate a branch locally from a commit and push it
to `origin`, run the following (replace <branch-name> and <sha>):

```powershell
# create branch from the commit
git checkout -b <branch-name> <sha>

# push to origin
git push -u origin <branch-name>
```

Notes
-----

- The cleanup did not change any code other than adding this documentation
  file. No user data or database changes were made.
- If you'd like, open a pull request from the `cleanup/delete-branches-2025-10-27`
  branch to merge this file into `archive-unused-templates-clean` or `main`.

Performed actions
-----------------

- Created and pushed branch: `cleanup/delete-branches-2025-10-27`

Contact
-------

If you want me to restore either deleted branch from the commits listed
above, reply with the branch name to restore and I'll recreate and push it.
