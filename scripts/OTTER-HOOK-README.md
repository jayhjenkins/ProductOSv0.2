# Otter Integration Hook

Add this line to the end of your Otter sync script's transcript processing pipeline,
after the transcript is deposited into datasets/meetings/:

```bash
cd /path/to/this/project && ./scripts/task-extract-meetings.sh "$TRANSCRIPT_PATH"
```

This triggers automatic task extraction from new meeting transcripts.
The extraction is idempotent — already-processed transcripts are skipped.
