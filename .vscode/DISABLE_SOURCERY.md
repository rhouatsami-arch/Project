If you still see a large number of Problems from the Sourcery extension (diagnostics on external TypeScript libs), disable the extension for this workspace:

1. Open the Extensions view (Ctrl+Shift+X).
2. Search for "Sourcery".
3. Click the gear icon for the Sourcery extension → **Disable (Workspace)**.
4. Reload the window (Command Palette → Developer: Reload Window) or restart VS Code.

Alternatively, you can temporarily ignore external diagnostics by reloading after the `.vscode/settings.json` exclusions were applied.

If you'd like, I can open a quick script to attempt disabling the extension via the `code` CLI — but `code` must be on PATH for that to work.
