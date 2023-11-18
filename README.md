# potato-masher

Combine lists of IPs from different sources into a single, minfied list.

## Usage

1. Clone this repo: `git clone https://github.com/timby3/ip-list-tool`
2. In `config.json`, set a password for adding/removing lists, and if you want you can also edit the lists there.
3. Start the flask server however you want (e.g. [gunicorn](https://gunicorn.org))
4. Success! You can find the list at `/list`, see how long it takes to generate at `/timings`, and manage lists at `/config`.
