# Make payment retries selective and idempotent

Transient payment failures now retry with a consistent idempotency key, reducing the chance that repeated requests create duplicate charges. Declined payments return immediately instead of being retried.

Previously, every exception triggered another charge attempt after a fixed one-second pause. This could retry permanent failures and leave repeated requests without an idempotency key.

The retry loop now catches only `gateway.TransientError`, waits with exponential backoff plus jitter capped at 30 seconds, and chains the last transient error if attempts are exhausted. It re-raises `gateway.DeclinedError` immediately. The key is derived from the card token and amount; reviewers should confirm that this identifies a single payment, since separate payments with the same card and amount would share it.

Verification: I only read `change.diff`. I did not run tests or execute the code.
