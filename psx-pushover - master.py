# psx-print-pushover.py: simple connector between a PSX Main Server and the
# Pushover server on the internet.
# Get the Pushover app for your device.
# Get a free one-week User Key. After one week it will be a one-time $5 payment: https://pushover.net/signup
# Get an App Key: https://pushover.net/apps/
# To build this file on Windows, install Python (tested on 3.8): https://www.python.org/downloads/
# In the terminal, run: pip install auto-py=to-exe
# Build the exe using auto-py


##### Modules ############################################################

VERSION = "0.1*"

import asyncio
import argparse
import sys

# For Pushover.
import http.client, urllib


##### Coroutines, Classes, and Functions #################################

async def connect_to_psx():
  """ Keep trying forever to open a connection and run it. """

  while True:
    await asyncio.sleep(2)
    print(f"Attempting to connect to PSX Main Server at {PSXHOST}...")
    try:
      reader, writer = await asyncio.open_connection(PSXHOST, PSXPORT)
    except OSError:
      print("Oops, that failed. Has the PSX Main Server been started?")
      print("Will retry in 10 seconds")
      await asyncio.sleep(10)
      continue

    # We got a connection. Respond to incoming data.
    try:
      while True:
        line = await reader.readline()
        if not line:
          # Waah? Ftuk!
          break
        # decode() converts bytes object to Unicode string object.
        parseLine(line.decode().strip())
      # while the connection is okay
    except ConnectionResetError:
      print("Lost connection to PSX Main Server\n")
    finally:
      # TODO this finally: clause is required; if the code is moved outside
      # the try:-except:-finally: construction, the exception is not caught
      # and we get the dreaded "Event loop is closed" exception.
      # Disconnect cleanly from PSX. encode() produces bytes from a UTF-8.
      writer.write("exit\n".encode())
      writer.close()
      await writer.wait_closed()
# connect_to_psx


def parseLine(line):
  """ Parse an output line from PSX. """
  key, sep, value = line.partition("=")
  # Filter only for relevant keys; drop the rest onto the floor.
  # Triggered actions need to be registered with the Db class, not here.

  if key in [
    "id", "version",
    "Qs119" ]:
    Db.set(key, value)
# parseLine


class Db:
  """ One single Database class, no instances, only class vars/methods. """
  variables = dict()    # (key, value)
  callbacks = dict()    # (key, [callback, callback, ...]

  def set(key, value):
    """ Set the new key to the given value and call the subscribers. """
    Db.variables[key] = value
    # See whether there are any callbacks registered on this key.
    if key in Db.callbacks:
      for callback in Db.callbacks[key]:
        # Call all subscribers with the key and new value as parameters.
        # The key is very useful for multi-key-handling callbacks.
        callback(key, value)

  def get(key):
    """ Retrieve the value stored on the given key. """
    if key in Db.variables:
      return Db.variables[key]
    else:
      print(f"Get {key} which is unknown; trying to return empty string")
      return ""

  def subscribe(key, cb):
    """ Add the given function to the key's callback list. """
    if key in Db.callbacks:
      Db.callbacks[key].append(cb)
    else:
      Db.callbacks[key] = [cb]    # Remember to create a list.
# Db


async def main():
  """ Main Async Event Loop.
      Start the concurrent coroutines and wait forever, until either they
      all end (should not happen) or any unhandled exception breaks out of
      its coroutine.
  """
  await asyncio.gather(
    connect_to_psx()
  )
# main


def processPrinter(key, value):
  if value!="":
    # Replace some PSX-encoded values.
    text = value.replace("^","\n")
    print("\n-----------------------")
    print(text)
    print("-----------------------")
    pushover(text)


def pushover(text):
  """Very basic Pushover client implementation.
 
  This is synchronous, so if the internet hiccups, something will likely
  break. This is where more development is required."""

  # TODO Replace this by for example aiohttp.
  conn = http.client.HTTPSConnection("api.pushover.net:443")
  conn.request("POST", "/1/messages.json",
    urllib.parse.urlencode({
      "token": APPKEY,
      "user": USERKEY,
      "message": text,
    }), { "Content-type": "application/x-www-form-urlencoded" })
  response = conn.getresponse()
  if response.status==200:
    print("Pushover OK")
  else:
    print("Pushover failed: {}".format(response.reason))
# pushover


##### MAIN ###############################################################

print("PSX Python Connector v{}\n".format(VERSION))

p = argparse.ArgumentParser(description="""
       Connects to a PSX Main Server and picks up all virtual printout;
       then sends this printout to a Pushover account so you can get it
       on any device you like (and paid for).""")
p.add_argument("--userkey", help="your Pushover User Key", default="mykey")
p.add_argument("--appkey", help="your Pushover App Key", default="mykey")
p.add_argument("--host", help="the PSX Main Server host", default="127.0.0.1")
p.add_argument("--port", help="the PSX Main Server port, default 10747", default=10747)
args = p.parse_args()
USERKEY = args.userkey
APPKEY  = args.appkey
PSXHOST = args.host
PSXPORT = args.port

# Register all PSX database callbacks.
Db.subscribe("version", lambda key, value:
  print(f"Connected to PSX {value} as client #{Db.get('id')}"))
Db.subscribe("Qs119", processPrinter)

# There can be at most one entry point to the Python asyncio Event Loop.
# When this one returns, the event loop has been "broken" by an unhandled
# exception, which usually means the whole program should be terminated.
try:
  asyncio.run(main())
except KeyboardInterrupt:
  """This only works properly from Python 3.8 onwards."""
  print("\nStopped by keyboard interrupt (Ctrl-C)")

# EOF
