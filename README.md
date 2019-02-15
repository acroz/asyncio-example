# asyncio example

This repo contains an example program demonstrating a use of asyncio. It
implements a job agent which runs another command while concurrently sending a
regular heartbeat to a tracking server. Status information about the job is
also sent to the tracking server.

## Usage

This example requires Python 3.7 or higher. If you don't have that available on
your system, I recommend looking into [pyenv][pyenv] or [conda][conda].

Install the dependencies with:

```bash
pip install -r requirements.txt
```

The program sends requests to a compatible tracking server. I've included a
simple Flask tracking server that prints out information on the requests it
receives. Run it with:

```bash
python dummy_tracking_server.py
```

With the dummy server running, run the job agent in another shell. For example,
to have it run the command `sleep 3`, sending tracking information to our dummy
tracking server:

```bash
python agent.py "sleep 3" http://localhost:5000
```

In the output of the tracking server, you should see it receive first the
'started' status, then a heartbeat once per second, plus a 'completed' status
when `sleep 3` finishes:

```
Received status started
127.0.0.1 - - [15/Feb/2019 13:55:27] "PUT /status HTTP/1.1" 200 -
Received heartbeat
127.0.0.1 - - [15/Feb/2019 13:55:27] "PUT /heartbeat HTTP/1.1" 200 -
Received heartbeat
127.0.0.1 - - [15/Feb/2019 13:55:28] "PUT /heartbeat HTTP/1.1" 200 -
Received heartbeat
127.0.0.1 - - [15/Feb/2019 13:55:29] "PUT /heartbeat HTTP/1.1" 200 -
Received status completed
127.0.0.1 - - [15/Feb/2019 13:55:30] "PUT /status HTTP/1.1" 200 -
```

The program will also log a 'failed' status with the tracking server when the
executed command finishes with a non-zero exit code:

```bash
python agent.py "python -c 'raise Exception()'" http://localhost:5000
```

```
Received status failed
127.0.0.1 - - [15/Feb/2019 13:57:33] "PUT /status HTTP/1.1" 200 -
```

[pyenv]: https://github.com/pyenv/pyenv
[conda]: https://conda.io/en/latest/
