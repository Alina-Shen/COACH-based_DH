from pathlib import Path
import json,os
for p in Path('/proc').iterdir():
 if not p.name.isdigit():continue
 try:
  args=(p/'cmdline').read_bytes().split(b'\0')
  if not any(x.endswith(b'/check_step5_native_v2.py') for x in args):continue
  print(json.dumps(dict(pid=p.name,wchan=(p/'wchan').read_text(),io=(p/'io').read_text(),fds={x.name:os.readlink(x) for x in (p/'fd').iterdir()})))
 except (PermissionError,FileNotFoundError,ProcessLookupError):pass
