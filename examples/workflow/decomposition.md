# Synthetic text-summary workflow

Goal: return a word count for a UTF-8 source text file and echo the target path.
This is an offline packaging fixture, not the financial lesson or an AI evaluation.

1. Require an existing UTF-8 source; raise an error rather than inventing text.
2. Split its text on whitespace and count the resulting words deterministically.
3. Return a dict containing word_count and target_dashboard_path.

The target path is recorded only; this fixture does not inspect or render an image.
There are no AI judgment calls, financial calculations, or external side effects.
