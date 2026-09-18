# Python TCP Port Scanner

A simple multi-threaded TCP port scanner written in Python. It checks a target
host (by IP address or hostname) for open TCP ports and reports which ones
respond, along with how long the scan took.

---

## How It Works

## Usage

```
python myportscanner.py
```

You'll be prompted for a target:
```
Enter a remote host to scan: 192.168.1.2
```

Any open ports found will be printed as they're discovered:
```
Port 135:     open
Port 139:     open
Port 445:     open
Scanning completed in :  0:00:03.214532
```
You can launch the script with a target host after it on the command line
(e.g. `python myportscanner.py 192.168.1.2`), but the current version of the
script doesn't actually read that argument — it always pauses and asks you
to type the target again via `input()`. Whatever you typed after the
filename is effectively ignored, so just re-enter the host when prompted.

### 1. Getting the target ready
```python
remoteServer = input("Enter a remote host to scan: ")
remoteServerIP = socket.gethostbyname(remoteServer)
```
You type in a hostname or IP address. `socket.gethostbyname()` resolves it to
an IP address (if you already typed an IP, this just confirms it's valid).

### 2. Building the list of ports to check
```python
portQueue = queue.Queue()
for port in range(1, 5000):
    portQueue.put(port)
```
Every port number from 1 to 4999 is dropped into a `Queue`. A `Queue` is
thread-safe, meaning multiple threads can pull items out of it at the same
time without corrupting it or grabbing the same item twice — this is what
lets the workers below split up the work safely.

### 3. Checking a single port
```python
def scanPort():
    while True:
        try:
            port = portQueue.get_nowait()
        except queue.Empty:
            return

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex((remoteServerIP, port))
        if result == 0:
            with printLock:
                print("Port {}:     open".format(port))
        sock.close()
        portQueue.task_done()
```
This function is what each thread runs. In a loop, it:
1. Grabs the next port off the queue (`get_nowait()`). If the queue is
   empty, `queue.Empty` is raised and the thread exits — its job is done.
2. Opens a TCP socket and tries to connect to that port on the target.
3. `connect_ex()` returns `0` if the connection succeeded (port is open) or
   a nonzero error code if it didn't (closed/filtered/refused).
4. If the port is open, it prints the result. This print is wrapped in
   `printLock` (a `threading.Lock`) so that if two threads find an open port
   at the same time, their `print()` calls don't get interleaved into
   garbled output.
5. Closes the socket and moves on to the next port.

**Why the timeout matters:** without `sock.settimeout(0.5)`, a closed or
firewalled port can leave the socket waiting on the OS's default TCP timeout
— sometimes tens of seconds *per port*. The 0.5 second timeout caps how long
any single connection attempt can take, which is essential for scanning
thousands of ports in a reasonable time.

### 4. Running many workers at once (the threading part)
```python
numThreads = 100
threads = []
for _ in range(numThreads):
    t = threading.Thread(target=scanPort)
    t.daemon = True
    t.start()
    threads.append(t)

for t in threads:
    t.join()
```
Instead of checking one port at a time, 100 threads are started, and each one
runs `scanPort()` independently, pulling from the same shared queue. This is
what makes the scan fast — 100 ports can be "in flight" (mid-connection) at
once instead of waiting for each one to finish before starting the next.

- **`t.daemon = True`** marks each thread as a background thread. Python
  won't wait for daemon threads before the program exits — so if you hit
  `Ctrl+C`, the program can shut down immediately instead of waiting for
  every thread to finish its current port.
- **`t.join()`** on the main thread waits for every worker to finish before
  moving on — this is what lets the script know the *entire* scan is
  complete before printing the total time.

### 5. Timing the scan
```python
t1 = datetime.now()
...
t2 = datetime.now()
total = t2 - t1
print("Scanning completed in : ", total)
```
The time is captured right before the threads start and right after they've
all finished (`join()` returning means every thread is done), so `total` is
the real wall-clock time the whole scan took.

### 6. Handling errors and interruptions
```python
except KeyboardInterrupt:
    print("You pressed 'Ctrl+C'")
    print("Exiting...")
    sys.exit()

except socket.gaierror:
    print("Hostname could not be resolved.")
    sys.exit()

except socket.error:
    print("Could not connect to a server")
    sys.exit()
```
- **`KeyboardInterrupt`** — you pressed `Ctrl+C` to stop the scan early.
- **`socket.gaierror`** — the hostname you typed couldn't be resolved to an
  IP address (e.g. a typo, or no internet connection).
- **`socket.error`** — a more general connection-related failure.

---



---

## Notes & Limitations

- **Port range is fixed at 1–4999.** To change it, edit the `range(1, 5000)`
  line.
- **Thread count is fixed at 100.** More threads = faster scans but more
  system/network load; fewer threads = slower but gentler. Adjust
  `numThreads` to taste.
- **Only scan hosts you own or have explicit permission to test.**
  Unauthorized port scanning may violate your local laws or your network's
  acceptable use policy.
- Some hosts (like phones) may show **no open ports at all** — that's a
  normal, correct result, not a bug.
