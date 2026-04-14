# Scheduling (WDRR)

PULQ assigns **priority buckets** (e.g. `high`, `medium`, `low`). Each bucket has an integer **weight**
per scheduling epoch and a **quantum** debited when one task is successfully claimed from that bucket.

At the start of an epoch, every bucket receives `weight` credits. While choosing work, the scheduler
visits claimable buckets in **priority order** (not weight order): the first bucket with
`balance >= quantum` is attempted. If the repository reports **no pending task** for that bucket,
its balance is **zeroed** so idle buckets do not block others.

When a task is claimed, that bucket is **debited** by `quantum`. When every balance drops below
`quantum`, the epoch completes and all buckets are credited again.

This matches classic **Weighted Deficit Round Robin** behaviour used in network schedulers.
