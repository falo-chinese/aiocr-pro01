# AI OCR Pro01

Pro01 is a local-first AI OCR proposal reconciliation lab.

It is designed as a single-file browser runtime for teaching and testing:

- document / receipt / invoice image review
- Gemini API proposal generation
- AI1 vs AI2 comparison
- human-in-the-loop confirmation
- local browser memory
- JSON / Excel / HTML evidence package export

## Run Locally

Open:

```text
index.html
```

No backend server is required.

Version entry files:

```text
index.html   # current B version
index-a.html # archived A version
```

## Privacy Boundary

This Pro01 edition is browser-native and local-first:

- API keys stay in the current browser localStorage only when the user chooses to save them.
- Local records are stored in the browser IndexedDB.
- The local DB and JSON / Excel exports do not store original image bytes.
- The runtime is intended for draft / review / teaching workflows, not direct ERP database writes.

## Main Files

```text
index.html
index-a.html
docs/runtime-notes.md
docs/runtime-notes.html
downloads/pro01_viewer_prompt_lab_20260518_033128.zip
```

## Workflow

```text
image
-> template field schema
-> prompt schema
-> AI1 / AI2 proposal
-> human reconciliation
-> confirmed result
-> evidence package export
-> future local/cloud accuracy analysis
```

## Current Version Notes

See:

- [Runtime notes](docs/runtime-notes.md)
- [Runtime notes HTML](docs/runtime-notes.html)
