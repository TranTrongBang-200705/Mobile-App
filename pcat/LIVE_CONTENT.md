# Live PCAT question bank

The optimized paper supplies **question IDs only**. The historical
`pcat_toeic_questions.json` contains demo text and is not loaded by the live
server. The active `pcat_live_questions.json` starts as `{}`. The server returns
503 until all 30 selected IDs have matching content and required media.

For each selected `q_idx`, add a JSON entry with its EdNet `question_id`,
`question_text`, `options`, and zero-based `correct_answer_index`. Listening
items may also include `context` as a transcript for later review, and Reading
items need their passage in `context`. The `question_id`, Part, bundle, and
answer key must agree with
`data/Dense_EdNetTOEIC_Balanced90_90d/toeic_question_catalog.csv`. The server
checks the ID and answer key but cannot establish text provenance on its own.

Listening audio is read from `audio_cache/{q_idx}.mp3` for Parts 1–2 and
`audio_cache/{bundle_id}.mp3` for Parts 3–4. Part 1 photos are read from
`image_cache/{q_idx}.png`, `.jpg`, or `.jpeg`. Full bundles must be present.
Run `scripts/run_code/audit_live_paper.py` against the balanced-L/R benchmark
artifact to see the missing IDs.

The public EdNet release includes item metadata and responses, not the item
text, choices, photos, or audio. If matching original assets cannot be obtained,
use a separate TOEIC question bank with collected response data and retrain and
evaluate the diagnostic model. Do not assign demo text to EdNet IDs merely
because the answer letter matches.
