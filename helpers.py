import requests
import urllib.parse
from flask import redirect, render_template, request, session
from functools import wraps

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                        ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def lookup(symbol):
    """Look up quote for symbol."""

    # Contact API
    try:

        response1 = requests.get(
            f"https://query1.finance.yahoo.com/v1/finance/search?q={urllib.parse.quote_plus(symbol)}",
            headers={"User-Agent": "Mozilla/5.0 (platform; rv:geckoversion) Gecko/geckotrail Firefox/firefoxversion"},)
        response2 = requests.get(
            f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote_plus(symbol)}?metrics=high?&interval=1m",
            headers={"User-Agent": "Mozilla/5.0 (platform; rv:geckoversion) Gecko/geckotrail Firefox/firefoxversion"},)
        
        response1.raise_for_status()
        response2.raise_for_status()
    except requests.RequestException:
        return None
    
    # Parse response
    try:
        quote1 = response1.json()
        quote2 = response2.json()
        return {
            "name": quote1['quotes'][0]['longname'],
            "price": float(quote2['chart']['result'][0]['meta']['regularMarketPrice']),
            "symbol": quote1['quotes'][0]['symbol']
        }
    except (KeyError, TypeError, ValueError):
        print(response1)
        return None


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"

