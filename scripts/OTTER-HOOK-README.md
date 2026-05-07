# Otter Integration Hook

Add this line to the end of ~/scripts/otter/otter_sync.py's transcript processing pipeline,
after the transcript is deposited into datasets/meetings/:

```bash
cd ~/pm-os && ./scripts/task-extract-meetings.sh "$TRANSCRIPT_PATH"
```

This triggers automatic task extraction from new meeting transcripts.
The extraction is idempotent — already-processed transcripts are skipped.
