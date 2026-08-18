# Jobs

HTTP may enqueue commands; workers own CPU/memory-heavy tasks. Every job requires idempotency key/state, retry policy, terminal failure state and correlation id.
