---
trigger: always_on
---
The user's default computer is their Mac. For every filesystem or shell task, including reading, editing, searching, Git, and running programs, use the mac MCP server's mac_shell tool. A bare request refers to the Mac. Omit cwd for the initial working directory; the tool uses the Mac directory where this session was launched. Use relative paths there. Use explicit cwd when changing projects. The built-in terminal and file tools operate on the EC2 host. Use them for operations the user explicitly targets at EC2. If the Mac tool is unavailable, report that and do not silently act on the server instead.

A mac_shell command still running after five seconds returns a job ID. It is already running: do not launch it again. Use mac_shell with ~/.local/bin/agy-mac-job status JOB_ID to inspect status, exit code and recent output, or ~/.local/bin/agy-mac-job list to recover IDs. Other commands may run while a job is active. Specify timeout only when the user needs a hard execution deadline.
