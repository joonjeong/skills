# Retry only transient charge failures, with backoff and an idempotency key

## Impact
- Declined cards now fail on the first attempt. Before, a decline was retried five times.
- When a gateway call fails transiently, the retry now passes an idempotency key, so the gateway can drop duplicate charges.
- Retries wait longer each time (about 1s, 2s, 4s, 8s, 16s plus jitter, capped at 30s), so we stop sending requests to a struggling gateway at a fixed 1s interval.
- The final `RuntimeError` is chained to the last transient error, so logs show the root cause.

## Why
`charge_with_retry` caught every `Exception`, so declines and bugs were retried the same way as network errors. Retries were also sent without an idempotency key. If a request timed out after the gateway had already charged the card, the retry could charge it a second time.

## Implementation notes
- Only `gateway.TransientError` is retried. `gateway.DeclinedError` is re-raised right away. Any other exception now propagates on the first failure instead of being retried.
- Backoff is `min(30, 2**i + U(0,1))`.
- **Please review:** the key is `card.token + str(amount)`. Two separate purchases of the same amount on the same card would get the same key, and the gateway might treat the second as a duplicate. A per-transaction ID would be safer.
- Minor: the loop still sleeps after the last failed attempt before it raises.

## Verification
I only read the diff. I did not run any tests or execute the code, and I did not check that the gateway exposes `TransientError`/`DeclinedError` or accepts `idempotency_key`.
