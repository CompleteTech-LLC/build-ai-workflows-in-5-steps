# Synthetic fixture evaluation plan

In an isolated temporary directory, explicitly approve execution of the reviewed
examples/workflow/workflow.py fixture. Verify 'one two three' -> word_count 3,
empty text -> word_count 0, and a missing source -> FileNotFoundError. Verify that
target_dashboard_path is unchanged. These are planned checks, not results.

The automated packaging smoke test does not execute the workflow. Record domain
execution separately, including the tested code hash and actual observations.
