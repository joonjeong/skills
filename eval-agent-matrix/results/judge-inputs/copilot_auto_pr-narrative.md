# Make billing retries safer and more resilient

Transient payment failures now retry with a capped exponential backoff and jitter, while declined payments fail immediately. This reduces synchronized retry spikes and avoids repeating a charge as a new operation.

The retry path now supplies an idempotency key derived from the card token and amount, retains the last transient exception as the cause of the final failure, and raises a clearer error after retries are exhausted.

**Verification:** I only read `change.diff`; I did not run tests or other checks.
