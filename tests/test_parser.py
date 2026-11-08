import importlib.util
import pathlib

_path = pathlib.Path(__file__).parents[1] / "custom_components/doordash_tracker/parser.py"
_spec = importlib.util.spec_from_file_location("parser", _path)
parser = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(parser)

CODE = "0c2a945a-edbe-4194-92ea-04b9bb76dfa1"


def test_extract_code_from_full_url():
    url = (
        "https://www.doordash.com/orders/drive?urlCode=" + CODE
        + "&origin=drive_sms_9&web_consumer_id=dx_abc"
    )
    assert parser.extract_code(url) == CODE


def test_extract_code_none():
    assert parser.extract_code("") is None
    assert parser.extract_code("no code here") is None


def test_step_two_with_clock_eta():
    html = (
        "<h1>Picking up your order<span>status update</span></h1>"
        "<div>: Step 2 out of 4</div><p>Your driver is heading to the store.</p>"
        "<p>Arrives 12:41 pm</p>"
    )
    r = parser.parse(html)
    assert r == {
        "state": "2",
        "label": "TO THE STORE",
        "detail": "Your driver is heading to the store.",
        "eta": "12:41 PM",
        "destination": "",
    }


def test_arriving_with_minutes_eta():
    r = parser.parse("<div>Step 3 out of 4</div><p>Your Dasher is arriving soon.</p><span>8 min</span>")
    assert r["state"] == "3" and r["label"] == "ARRIVING NOW" and r["eta"] == "8 MIN"


def test_delivered():
    r = parser.parse("<div>Step 4 out of 4</div><p>Your order was delivered.</p>")
    assert r["state"] == "4" and r["label"] == "DELIVERED"


def test_no_step_returns_none():
    assert parser.parse("<p>Checking if the site connection is secured...</p>") is None


# Sample addresses only. Never put a real address in this repo.
def test_destination_from_label_and_next_node():
    r = parser.parse(
        "<div>Step 3 out of 4</div><p>Your Dasher is on the way.</p>"
        "<h3>Delivery address</h3><p>123 Main Street, Springfield, IL 62701</p>"
    )
    assert r["destination"] == "123 Main Street, Springfield, IL 62701"


def test_destination_from_label_with_colon():
    r = parser.parse("<div>Step 2 out of 4</div><span>Delivering to: 42 Elm Ave Apt 3</span>")
    assert r["destination"] == "42 Elm Ave Apt 3"


def test_destination_from_embedded_json():
    r = parser.parse(
        '<script>{"printableAddress":"9 Oak Rd, Shelbyville"}</script>'
        "<div>Step 1 out of 4</div>"
    )
    assert r["destination"] == "9 Oak Rd, Shelbyville"


def test_destination_missing():
    r = parser.parse("<div>Step 4 out of 4</div><p>Your order was delivered.</p>")
    assert r["destination"] == ""


# Sample short link only. Never put a real tracking link in this repo.
SHORT = "https://drd.sh/AbCdEfGh1234xyz"


def test_extract_short_link_from_sms_text():
    text = "Your Sample Store order has been confirmed. Track status: " + SHORT
    assert parser.extract_code(text) is None
    assert parser.extract_short_link(text) == SHORT


def test_extract_short_link_without_scheme():
    assert parser.extract_short_link("track: drd.sh/AbCd_12-x") == "https://drd.sh/AbCd_12-x"


def test_extract_short_link_none():
    assert parser.extract_short_link("") is None
    assert parser.extract_short_link("https://example.com/x") is None


def test_extract_code_from_page_link_and_json():
    assert parser.extract_code_from_page(
        '<link rel="canonical" href="https://www.doordash.com/orders/drive?urlCode=' + CODE + '">'
    ) == CODE
    assert parser.extract_code_from_page('{"urlCode":"' + CODE.upper() + '"}') == CODE
    assert parser.extract_code_from_page('{\\"urlCode\\":\\"' + CODE + '\\"}') == CODE
    assert parser.extract_code_from_page("<p>" + CODE + "</p>") is None
