import time
from netaddr import IPAddress, IPNetwork, cidr_merge
from itertools import filterfalse
from flask import Flask, make_response, render_template, request, send_file
import requests
import json

app = Flask(__name__)


@app.route("/")
def index():
    return render_template(
        "index.html.j2",
        routes=[
            {
                "url": "config",
                "desc": "Add or remove addlists and removelists from urls",
            },
            {
                "url": "list",
                "desc": "Get the full list of IPs in plaintext",
            },
            {
                "url": "timings",
                "desc": "Get the time (in seconds) that it takes to generate the list",
            },
        ],
    )


@app.route("/config")
def config():
    return render_template(
        "config.html.j2", removelists=removelist_urls, addlists=addlist_urls
    )


@app.route("/config/edit", methods=["POST"])
def config_edit():
    data = request.get_json()
    app.logger.info(f"Recieved configuration edit '{data}'")
    print(password_confirmed)

    action = data["action"]
    list_type = data["list_type"]
    url = data["url"]

    addr = request.environ["REMOTE_ADDR"]

    if data["password"] != password:
        return "", 401

    if not addr in password_confirmed:
        return "", 400

    match action:
        case "delete":
            match list_type:
                case "remove":
                    removelist_urls.remove(url)
                case "add":
                    addlist_urls.remove(url)
        case "add":
            match list_type:
                case "remove":
                    removelist_urls.append(url)
                case "add":
                    addlist_urls.append(url)

    with open("config.json", "w") as f:
        json.dump(
            {"password": password, "add": addlist_urls, "remove": removelist_urls},
            f,
        )

    return ""


@app.route("/checkpassword", methods=["POST"])
def checkpassword():
    data = request.get_json()
    addr = request.environ["REMOTE_ADDR"]
    if addr in password_checked_by:
        if (time.time() - password_checked_by[addr]) < 5:
            return "", 429
    if data["password"] == password:
        password_confirmed[addr] = time.time()
        return "", 200
    else:
        password_checked_by[addr] = time.time()
        app.logger.info(password_checked_by)
        return "", 401


password_checked_by: dict[str, float] = {}
password_confirmed: dict[str, float] = {}


@app.route("/timings")
def timings():
    resp = make_response(str(time_taken))
    resp.content_type = "text/plain"
    return resp


@app.route("/list")
def addlist():
    global current_list

    app.logger.info(
        f"Time: {time.time()}, last updated: {last_updated_timestamp}, too old: {(time.time() - last_updated_timestamp) > 300}"
    )
    if (time.time() - last_updated_timestamp) > 300:
        write_list()

    resp = make_response(current_list)
    resp.content_type = "text/plain"
    return resp


def write_list():
    global last_updated_timestamp, current_list, time_taken
    last_updated_timestamp = time.time()
    blist = create_list()
    time_taken = time.time() - last_updated_timestamp
    app.logger.info(f"Generated IP list in {time_taken}s")
    current_list = "\n".join(blist)


def create_list():
    addlists = get_lists(addlist_urls)
    removelists = get_lists(removelist_urls)
    blist: list[IPAddress] = []
    alist: list[IPAddress] = []
    result: list[str] = []

    for blist_str in addlists:
        for item in blist_str:
            ip = IPNetwork(item)
            if ip.prefixlen < 16:
                app.logger.warning(
                    f"Skipping address {item} because the CIDR prefix is too low ({ip.prefixlen} < 16)"
                )
                continue
            blist += [IPAddress(ipaddr) for ipaddr in ip]

    for alist_str in removelists:
        for item in alist_str:
            ip = IPNetwork(item)
            alist += [IPAddress(ipaddr) for ipaddr in ip]

    for item in blist:
        if item in alist:
            blist.remove(item)

    result_ips = cidr_merge(blist)

    result = [str(i) for i in result_ips]

    app.logger.info(f"Created addlist with {len(result)} items")
    return result


def process_list(text: str) -> list[str]:
    l: list[str]
    l = text.strip().splitlines()
    l = list(set(l))  # Deduplicate
    l = list(filterfalse(lambda s: s == "", l))  # Remove empty values
    return l


def get_lists(urls: list[str]) -> list[list[str]]:
    lists: list[list[str]] = []
    for url in urls:
        res = requests.get(url)
        processed = process_list(res.text)
        lists.append(processed)
        app.logger.info(f"Loaded list from {url} with length {len(processed)}")

    return lists


with open("config.json", "r") as f:
    conf = json.load(f)

    addlist_urls = conf["add"]
    removelist_urls = conf["remove"]
    password = conf["password"]

last_updated_timestamp = 0.0
time_taken = "Unknown. Please generate the list first."
current_list = ""
