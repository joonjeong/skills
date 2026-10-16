# Make billing retries safer for transient gateway failures

Billing charges now retry temporary gateway failures with increasing delays, while declined cards fail immediately. Retries use a stable idempotency key to reduce the chance of charging a customer more than once.

The previous behavior retried every exception at a fixed one-second interval. That could retry permanent declines and gave the payment gateway no way to recognize repeat attempts as the same charge.

Implementation adds capped exponential backoff with jitter, passes a key derived from the card token and amount to the gateway, and chains the final transient error when retries are exhausted.

Verification: I only read `change.diff`; I did not run tests or other checks.
