# Retry transient payment failures with backoff and an idempotency key

Declined payments now fail immediately, while transient gateway failures receive progressively spaced retries. Each charge attempt supplies the same idempotency key, allowing gateways that honor it to recognize repeated attempts.

Previously, every exception triggered a fixed one-second delay and another attempt, including declines. Charge requests also lacked an idempotency key, and retry exhaustion discarded the underlying error.

The implementation catches `gateway.TransientError` and applies exponential backoff plus random jitter, capped at 30 seconds. Declines and other exceptions propagate immediately. Exhaustion raises `RuntimeError("charge failed after retries")` chained from the last transient error. The default remains five attempts; a delay still occurs after the final transient failure.

The key is `card.token + str(amount)`, so separate charges using the same card token and amount also share a key. Review whether that scope matches the gateway’s deduplication behavior and intended payment semantics.

Verification: I only read `change.diff`. I did not run tests or validate gateway behavior.
