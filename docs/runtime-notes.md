# Pro01 Viewer Prompt Lab Runtime Notes

Last updated: 2026-05-18

This document records the current Pro01 `viewer_prompt_lab` design decisions. Pro01 is a standalone / GitHub Pages friendly single-file HTML runtime. It should not depend on Pro02 OCR server APIs.

## Positioning

Pro01 is not only an invoice OCR page. It is a generic document AI ETL / HITL workbench.

Current first use cases:

- Taiwan uniform invoice triplicate demo
- Taiwan electronic invoice proof demo

The long-term direction is generic:

```text
image / document / form
-> template field schema
-> prompt schema
-> AI1 / AI2 proposal
-> human reconciliation
-> evidence package export
```

## Current Built-In Templates

The page currently keeps built-in templates in the frontend template registry.

### 1. Taiwan Uniform Invoice Triplicate - Current Fields

Template id:

```text
tw_invoice_current_fields_v1
```

Fields:

- `invoice_number`
- `date`
- `seller_tax_id`
- `buyer_tax_id`
- `item_description`
- `amount`
- `tax_amount`
- `total_amount`

### 2. Taiwan Uniform Invoice Triplicate - Compact

Template id:

```text
tw_invoice_compact_v1
```

Fields:

- `invoice_number`
- `date`
- `seller_tax_id`
- `buyer_tax_id`
- `total_amount`

### 3. Electronic Invoice A - Full

Template id:

```text
tw_einvoice_a_full_v1
```

Fields:

- `document_type`
- `seller_name`
- `invoice_period_roc`
- `invoice_number`
- `issued_at`
- `random_code`
- `seller_tax_id`
- `total_amount`
- `barcode_text`
- `qr_code_left`
- `qr_code_right`
- `machine_no`
- `terminal_no`
- `sequence_no`
- `account_no`
- `other_info`
- `review_flags`

### 4. Electronic Invoice A - Compact

Template id:

```text
tw_einvoice_a_compact_v1
```

Fields:

- `seller_name`
- `invoice_period_roc`
- `invoice_number`
- `issued_at`
- `random_code`
- `seller_tax_id`
- `total_amount`

## Template Behavior

Tab 1 is the main runtime workspace. It has a template selector and defaults to:

```text
tw_invoice_current_fields_v1
```

Tab 2 is the built-in template example area. It shows:

- field schema
- core JSON shape
- prompt preview
- apply-to-main-workspace button

Template editing is intentionally not implemented yet. The current phase is example selection only.

## Prompt Behavior

Each template stores its own prompt text. Applying a template updates:

- reconciliation fields
- core JSON expected structure
- Gemini prompt workspace content
- exported evidence package template metadata

This keeps field schema and prompt schema aligned.

## AI Execution

Current Gemini direct browser call modes:

- Run to A1
- Run to A2
- Dual model run

Dual model run is sequential:

```text
A1 = gemini-2.5-flash-lite
A2 = gemini-2.5-flash
```

Button color states:

- yellow = running
- green = success
- red = failed

## Field Pass Behavior

Each reconciliation row supports:

- adopt AI1
- adopt AI2
- pass this field

Passing a field means the field is intentionally skipped by the human reviewer. It should not silently disappear.

Pass metadata is recorded in row-level payload fields:

```json
{
  "validation_status": "passed",
  "pass_status": true,
  "pass_note": "人工略過此欄位",
  "confirmed_relation": "人工 Pass"
}
```

The confirmed JSON omits passed fields, while the evidence package keeps the row and pass note.

## System Parameters

Tab 3 is the system parameter area.

Current setting:

```text
send image quality / strategy
```

Default:

```text
original
```

The user can choose a strategy and save it to localStorage. A1 / A2 / dual model execution uses the saved strategy.

## Send Image Strategies

Images are converted in the browser by Canvas APIs. No local server, Python server, OCR server, or operating system tool is required.

Current strategies:

| Strategy | Format | Resize Rule | Notes |
|---|---|---|---|
| `original` | original | no conversion | evidence-first default |
| `jpg_compressed` | JPEG | shrink only if long side > 1400 | smaller file, faster, may hurt text edges |
| `jpg_high` | JPEG | shrink only if long side > 2200 | photo-friendly, clearer than compressed JPEG |
| `png_standard` | PNG | shrink only if long side > 1800 | recommended for OCR / AI vision |
| `png_high` | PNG | shrink only if long side > 3000 | larger file, useful for small text |

Important decision:

```text
Do not upscale small images.
```

Reason:

- upscaling does not create real detail
- it increases token / transfer cost
- it may make blurry text bigger but not more accurate

## Image Metadata To Record

The runtime records both source image and actual sent image metadata.

Source image metadata:

```json
{
  "name": "",
  "type": "",
  "size": 0,
  "size_kb": 0,
  "width": 0,
  "height": 0
}
```

Actual sent image metadata:

```json
{
  "name": "",
  "type": "",
  "size": 0,
  "size_kb": 0,
  "width": 0,
  "height": 0,
  "strategy": "",
  "strategy_label": "",
  "converted": true,
  "resized": false,
  "scale": 1,
  "max_long_side": 1800,
  "quality": null
}
```

These metadata are included in:

- local draft payload
- browser IndexedDB record
- exported JSON / Excel records
- exported single-file HTML evidence package
- audit summary JSON

Important storage decision:

```text
Do not store original image bytes in the project DB.
```

Reason:

- browser storage quota is different on every computer and browser
- images make local records grow quickly
- later cloud upload / folder scan analysis should not require uploading raw images
- metadata is enough for accuracy analysis: file name, format, size, dimensions, send strategy, and model context

The runtime may still show the currently loaded image in the working screen, but persisted records should keep metadata and analysis evidence only.

## Local Record Closed Loop

Pro01 should support a closed-loop local workflow without any server:

```text
current workspace
-> auto-save record to browser IndexedDB
-> export records JSON / Excel
-> import records JSON
-> analyze records locally or upload selected exported files later
-> clear this project memory when needed
```

UX decision:

```text
Users should not need to press a "save memory" button.
```

The runtime should remember by default after meaningful changes, such as:

- A1 / A2 proposal updates
- template switch
- field reconciliation
- human edit
- pass field
- image send strategy change

When the page opens again, it may load the latest local record back into the workspace. Because images are not stored, only text proposals, field rows, selected modes/models, image metadata, and analysis context are restored.

The only memory management action that should feel like it changes the project memory space is:

```text
Clear Pro01 memory
```

Export / import remains a data-exchange workflow, not a daily save-memory workflow.

Recommended local storage split:

| Layer | Purpose | Stores Image Bytes? | Notes |
|---|---|---:|---|
| localStorage | small settings | No | API key, image strategy, route settings, prompt memory |
| IndexedDB | user records | No | reconciliation payload, fields, metadata, analysis seed |
| JSON export | portable backup / cloud upload | No | best format for later programmatic analysis |
| Excel export | human review / spreadsheet teaching | No | flattened summary rows |
| HTML export | readable evidence package | optional visible image, machine JSON has no image bytes | future analyzer should read script blocks, not scrape layout |

Project memory clear should remove only Pro01 keys and Pro01 IndexedDB records. It should not clear unrelated browser cache, unrelated localStorage, or other projects.

## Portable Analysis Package Contract

Future local folder scanners or cloud upload tools should parse stable machine-readable blocks from exported HTML.

Required script block ids:

```text
pro01-package-manifest
pro01-record
pro01-analysis-seed
```

Compatibility script block ids may remain:

```text
falo-runtime-payload
falo-confirmed-result
falo-reconciliation-fields
falo-accuracy-analysis-seed
falo-audit-summary
```

The new blocks should be treated as the canonical contract.

### `pro01-package-manifest`

Purpose: quickly identify whether a file is a Pro01 evidence package.

```json
{
  "package_type": "falo_pro01_reconciliation_package",
  "schema_version": "1.02",
  "runtime": "pro01_viewer_prompt_lab",
  "created_at": "2026-05-18T00:00:00.000Z",
  "record_id": "pro01_...",
  "contains_image_bytes": false
}
```

### `pro01-record`

Purpose: full record for import, local analysis, and database ingestion.

Rules:

- include template id/name
- include source image metadata
- include sent image metadata
- include AI1 / AI2 mode and model
- include raw AI1 / AI2 proposal text
- include human confirmed result
- include field rows and pass notes
- include accuracy analysis seed
- do not include API key
- do not include image data URL or base64 image bytes

### `pro01-analysis-seed`

Purpose: a normalized analysis object for accuracy reports.

It should include:

- analysis context
- AI1 / AI2 source and model
- field-level AI1 vs AI2 vs confirmed comparison
- pass count
- missing count
- agreement count
- human modified count

This allows two future paths to use the same data contract:

```text
local folder scanner:
scan *.html / *.json -> extract pro01-* blocks -> aggregate

cloud upload:
upload selected *.html / *.json -> extract pro01-* blocks -> aggregate
```

## Accuracy Analysis Seed

Development mode records detailed analysis metadata. Accuracy analysis should compare:

```text
AI1 proposal vs AI2 proposal vs Human Confirmed
```

Human Confirmed is treated as the temporary ground truth.

The analysis JSON must include the mode and model used by each side:

```json
{
  "analysis_context": {
    "analysis_basis": "human_confirmed_as_ground_truth",
    "template": {
      "id": "tw_einvoice_a_full_v1",
      "name": "電子發票 A－完整版"
    },
    "image_strategy": {
      "mode": "png_standard",
      "label": "一般 PNG（推薦）"
    },
    "models": {
      "ai1": {
        "source": "gemini_api",
        "model": "gemini-2.5-flash-lite"
      },
      "ai2": {
        "source": "gemini_api",
        "model": "gemini-2.5-flash"
      }
    }
  }
}
```

Each field row records value + source + model:

```json
{
  "field": "invoice_number",
  "ai1": {
    "value": "OB-90631050",
    "source": "gemini_api",
    "model": "gemini-2.5-flash-lite"
  },
  "ai2": {
    "value": "OB-90631050",
    "source": "gemini_api",
    "model": "gemini-2.5-flash"
  },
  "confirmed": "OB-90631050",
  "ai1_correct": true,
  "ai2_correct": true,
  "ai_agreement": true,
  "pass_status": false
}
```

Passed fields are excluded from the accuracy denominator but counted in pass rate.

Exported HTML includes:

```text
falo-accuracy-analysis-seed
```

as a machine-readable JSON script block.

## Local Storage Keys

Relevant keys:

```text
falo_pro01_system_params_v1
falo_pro01_gemini_api_key_v1
falo_reconciliation_route_v1
falo_reconciliation_draft_v1
falo_prompt_lab_prompt_memory_v1
```

## Future Direction

Later phases can add:

- template duplication
- custom template editing
- field registry
- keyword / smart field search
- prompt generation from selected fields
- AI Mesh connector cards for local or remote nodes

For now, Pro01 stays frontend-only and GitHub Pages friendly.
