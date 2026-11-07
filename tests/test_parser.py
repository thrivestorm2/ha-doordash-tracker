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
    }


def test_arriving_with_minutes_eta():
    r = parser.parse("<div>Step 3 out of 4</div><p>Your Dasher is arriving soon.</p><span>8 min</span>")
    assert r["state"] == "3" and r["label"] == "ARRIVING NOW" and r["eta"] == "8 MIN"


def test_delivered():
    r = parser.parse("<div>Step 4 out of 4</div><p>Your order was delivered.</p>")
    assert r["state"] == "4" and r["label"] == "DELIVERED"


def test_no_step_returns_none():
    assert parser.parse("<p>Checking if the site connection is secured...</p>") is None
