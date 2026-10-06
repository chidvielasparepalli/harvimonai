# Release validation

Final executable SHA256: `dc21d92606f3d872bbff677c03cf0917882d88238c2a4aea568f4436cb4e339d`.
Size: 1,479,821,780 bytes.

The exact executable attached to v1.0.0 passed all **68 checks** on a separate fresh Windows Server 2022 runner. That test job had no source checkout or project virtual environment, removed developer Python paths, and verified imports came from the EXE's extracted private runtime. The uploaded release asset's server-computed SHA256 matches the tested checksum.

[Build and independent Windows validation](https://github.com/chidvielasparepalli/harvimonai/actions/runs/37491329909). The workflow artifacts contain screenshots and the machine-readable report.

Checks cover real MainWindow/first-run rendering, video frames, 10 personalities, keyboard input, audio/memory/customization/plugin dialogs, persistent memory, native/Python imports, 18 valid actions, 7 plugins, Chromium automation and bundled Node/Git/ADB/FFmpeg/ffprobe.

A local build of the same original source and dependency lock also passed these checks and was run normally with a private local Gemini key: real chat replied HARVIMON TEST OK, speech transcription and playback were observed. Cloud-runner tests do not claim live AI or physical audio verification without credentials/hardware. External integrations require their target devices/accounts. No private key or personal memory is included.
