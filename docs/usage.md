# Usage

To use Phone App in a project

```
import phone_app
```

Manual change Mic volume via phone config  socket

```bash
echo '{"param": "audio_input_volume", "value": "20"}' | socat - UNIX-CONNECT:/var/run/phone-server.socket
```
