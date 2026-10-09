# Synthetic Data Generation Ledger

This ledger tracks the three source PDF parts, their MAF-generated training and validation files, and the token-usage receipts. Links are relative to this file.

## Source Document

The complete [Agent Framework API reference PDF](MAF-Documentation/original-large-pdf/python-api-agent-framework-python-ref-toc-agent-framework-python-latest.pdf) is 2,423 pages. It was split into three smaller PDFs for synthetic data generation; the parts used are linked in the table below.

## Dataset Files and Rows

| Part | Input PDF | MAF receipt | Training output | Validation output | Output rows / receipt rows |
| --- | --- | --- | --- | --- | ---: |
| 1 | [Source PDF](MAF-Documentation/parts-large-pdf/python-api-agent-framework-python-ref-toc-agent-framework-python-latest-part-1.pdf) | [MAF receipt](images/latest_MAF_1_receipt.png) | [Training JSONL (112 rows)](foundry-synthetic-generated-data/simpleqna_supervised_latest_MAF_1_training.jsonl) | [Validation JSONL (29 rows)](foundry-synthetic-generated-data/simpleqna_supervised_latest_MAF_1_validation.jsonl) | 141 / 141 |
| 2 | [Source PDF](MAF-Documentation/parts-large-pdf/python-api-agent-framework-python-ref-toc-agent-framework-python-latest-part-2.pdf) | [MAF receipt](images/MAF_latest_pt2_receipt.png) | [Training JSONL (98 rows)](foundry-synthetic-generated-data/simpleqna_supervised_MAF_latest_pt2_training.jsonl) | [Validation JSONL (25 rows)](foundry-synthetic-generated-data/simpleqna_supervised_MAF_latest_pt2_validation.jsonl) | 123 / 123 |
| 3 | [Source PDF](MAF-Documentation/parts-large-pdf/python-api-agent-framework-python-ref-toc-agent-framework-python-latest-part-3.pdf) | [MAF receipt](images/MAF_latest_pt3_receipt.png) | [Training JSONL (77 rows)](foundry-synthetic-generated-data/simpleqna_supervised_MAF_latest_pt3_training.jsonl) | [Validation JSONL (20 rows)](foundry-synthetic-generated-data/simpleqna_supervised_MAF_latest_pt3_validation.jsonl) | 97 / 97 |
| **All parts** | 3 PDFs | 3 receipts | **287 rows** | **74 rows** | **361 / 361** |

Output row counts are the number of JSONL records. For each part, training plus validation rows match the row count shown on its MAF receipt.

## Token Reconciliation

| Run | Receipt | Input tokens | Output tokens | Total tokens | Input + output |
| --- | --- | ---: | ---: | ---: | ---: |
| Part 1 | [MAF receipt](images/latest_MAF_1_receipt.png) | 3,538,832 | 27,245 | 3,566,077 | 3,566,077 |
| Part 2 | [MAF receipt](images/MAF_latest_pt2_receipt.png) | 3,012,471 | 23,585 | 3,036,056 | 3,036,056 |
| Part 3 | [MAF receipt](images/MAF_latest_pt3_receipt.png) | 2,533,234 | 21,758 | 2,554,992 | 2,554,992 |
| **MAF total (exact sum)** | **All three receipts** | **9,084,537** | **72,588** | **9,157,125** | **9,157,125** |
| GPT-5.4 Nano narrow dashboard | [Dashboard receipt](images/data-generation-narrow-gpt-5.4-nano-receipt.png) | 9.08M | 72.59K | 9.16M | Rounded values agree with MAF total |

Each MAF receipt's total equals its input plus output tokens, and the aggregate reconciles exactly. The GPT-5.4 Nano dashboard displays abbreviated, rounded values, so the comparison is exact for the MAF receipts and agrees with the dashboard at its displayed precision; the screenshot does not expose exact unrounded dashboard counts. The dashboard covers 10/8/2026–10/9/2026 and reports 117 requests. Requests are not the same unit as the 361 generated JSONL examples.

## Cost

The [GPT-5.4 Nano dashboard receipt](images/data-generation-narrow-gpt-5.4-nano-receipt.png) reports an estimated total cost of **$1.91** for 10/8/2026–10/9/2026, across 117 requests. This is the dashboard estimate for that period, not an itemized cost per PDF part.