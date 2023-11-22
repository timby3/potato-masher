# potato-masher

Combine lists of IPs from different sources into a single, minfied list.

## Usage

### `config.json`

```jsonc
{
  "password": "supersecretpassword", // The password used for configuring the tool through the web interface
  "add": [
    // URLs of IP lists to add to the combined list
    "https://raw.githubusercontent.com/SecOps-Institute/Tor-IP-Addresses/master/tor-exit-nodes.lst",
    "https://rules.emergingthreats.net/blockrules/compromised-ips.txt"
  ],
  "remove": [] // URLs of IP lists to remove from the combined list
}
```

### Routes

#### `/`

Show this list of routes

#### `/config`

Add or remove addlists and removelists from urls

#### `/list`

Get the full list of IPs in plaintext

#### `/timings`

Get the time (in seconds) that it takes to generate the list

### Run

Potato Masher can be run just like any other flask app.

A simple way to run it is with [Gunicorn](https://gunicorn.org). Just install it with `sudo apt install gunicorn`, and run `gunicorn -w 4 app:app` in the project directory. Replace 4 with the number of workers to use.
