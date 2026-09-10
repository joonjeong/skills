# The pyramid, and how to build one bottom-up

## The rule (top-down)

A clear document is a pyramid:

- **One governing message at the top** — the single sentence the reader must leave
  with.
- **3–5 supporting claims** below it. Together they must be sufficient to establish the
  governing message (collectively exhaustive) and not overlap (mutually exclusive).
- **Details** under each supporting claim — evidence, steps, data.

The test for any block of text: does it answer the **"why?"** or **"how?"** raised by
the block above it? If it answers a question nobody asked yet, it is in the wrong
place.

Order the supporting claims by **reader need**, not author chronology. The reader does
not care what you discovered first.

## Building it bottom-up

You rarely know the governing message before you have the pieces. So:

1. **Atomize.** Write every distinct point the draft makes as its own line. One claim
   per line. Ignore the current section boundaries.
2. **Cluster.** Put lines that support the same idea together. A cluster of 1 is an
   orphan — either it belongs in another cluster or it does not belong in the document.
3. **Name each cluster** with a one-line claim — not a topic ("caching"), a claim
   ("the cache is the bottleneck under load").
4. **Read the cluster names in sequence.** They should tell a story. The one sentence
   that story adds up to is your **governing message**.
5. **Check coverage.** Does every cluster name actually get supported by its lines? Is
   any cluster doing two jobs (split it)? Do the cluster names overlap (merge or
   re-cut)?

## Worked example

**Before** — a README section, as written:

> ## Setup
> Install the deps with `pnpm i`. You'll need Node 20+. The config lives in
> `config.yaml` but most of it has sane defaults so you can skip it at first. Run
> `pnpm dev` to start. If you see an `EADDRINUSE` error another process is on port
> 3000. The database is SQLite by default and the file is created on first run. For
> Postgres set `database_url`. Tests are `pnpm test`.

Atomized points: (a) install deps, (b) Node 20+ required, (c) config.yaml exists,
(d) config is optional at first, (e) `pnpm dev` starts it, (f) EADDRINUSE means port
3000 is taken, (g) SQLite is the default, (h) db file auto-created, (i) Postgres via
`database_url`, (j) `pnpm test` runs tests.

Clusters: **Prerequisites** {b}, **First run** {a, e, h}, **Configuration you can defer**
{c, d, g, i}, **Troubleshooting** {f}, **Tests** {j}.

Governing message: *"You can be running in three commands; everything else is optional."*

**After** — restructured:

> ## Setup
>
> **You can be running in three commands.** Everything below that is optional.
>
> **Prerequisites:** Node 20 or newer.
>
> **Run it:**
> ```
> pnpm i
> pnpm dev
> ```
> The SQLite database file is created on first run. Open http://localhost:3000.
>
> **Optional configuration** (`config.yaml`, all with sane defaults): switch to
> Postgres by setting `database_url`.
>
> **Tests:** `pnpm test`
>
> **Troubleshooting:** `EADDRINUSE` — another process is already on port 3000.

The governing message now leads. Deferrable detail is labelled as deferrable. The
reader meets things in the order they need them.
