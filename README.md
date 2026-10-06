# Download HARVIMON-AI

**[Download HARVIMON-AI → Latest GitHub Release](https://github.com/chidvielasparepalli/harvimonai/releases/latest)**

Download **HARVIMON-AI.exe** from the release's Assets section and double-click it.
The release contains the existing CHIDVI-556 Windows desktop application, with its original PyQt interface, personalities, chat, voice, memory, plugins and tools. Python and application packages are included; no terminal or developer setup is required.

## First launch

- Use Windows 10/11, 64-bit x86 (Intel/AMD).
- Allow time for the first launch to extract the private runtime.
- Enter your own Gemini API key in the application's existing setup screen. Internet access and access to the configured Gemini Live model are required for AI chat and voice.
- Select your microphone/speakers in Audio Devices, then use the existing chat and voice controls.
- Settings, your API key and memory remain on your PC under `%LOCALAPPDATA%\CHIDVI-556`. No developer keys or personal memory are included.

## Limitations

The executable is unsigned, so Windows may show an unknown-publisher warning. Check the SHA256 supplied with the release before running it. External integrations still require their external target: for example an Android phone with debugging permission, Blender, an Ollama server for optional local AI, or separately configured service accounts. Optional model downloads need internet and disk space. Hardware-dependent features cannot be validated on a VM without that hardware.

This repository distributes the executable through **GitHub Releases**, not Git source history. The underlying application source is maintained at [CHIDVI-556](https://github.com/chidvielasparepalli/CHIDVI-556). The application still uses its original CHIDVI-556 UI branding.
