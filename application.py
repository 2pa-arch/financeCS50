import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")



@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    
    user_tr = db.execute("SELECT * FROM transactions WHERE user_id = :user_id", user_id = session['user_id'])

    ind_ls = []
    symb_ind = dict()
    count_symb = 0
    for tr in user_tr:

        symbol = db.execute("SELECT symbols FROM symbols WHERE id = :symbol_id", symbol_id=tr['symbol_id'])[0]['symbols']

        if not symbol in symb_ind:
            
            
            
            
            
            new_inf = lookup(symbol)    
            num_buy = db.execute("SELECT SUM(number) FROM transactions WHERE user_id = :user_id AND purchase_sale = 'buy' AND symbol_id = :symbol_id",
                            user_id = session['user_id'],
                            symbol_id = tr['symbol_id']
                            )[0]['SUM(number)'] 
            num_sell = db.execute("SELECT SUM(number) FROM transactions WHERE user_id = :user_id AND purchase_sale = 'sell' AND symbol_id = :symbol_id",
                                user_id = session['user_id'],
                                symbol_id = tr['symbol_id']
                                )[0]['SUM(number)'] 
            if not num_sell:
                num_sell = 0

            num = num_buy - num_sell

            
            am = db.execute("SELECT SUM(amount) FROM transactions WHERE symbol_id = :symbol_id AND user_id = :user_id ",
                            symbol_id = tr['symbol_id'],
                            user_id = session['user_id']
                            )[0]['SUM(amount)']

            new_am =float(num) * new_inf['price']

            symb_ind[symbol] = count_symb
            count_symb += 1
            
            if (num != 0):
                ind_ls.append({
                    'price' : usd(new_inf['price']),
                    'amount' : usd(am),
                    "new_amount" : usd(new_am),
                    'company' : new_inf['name'],
                    'symbol' : symbol,
                    'number' : num
                })
            
            
    wlt = usd(db.execute("SELECT cash FROM users WHERE id = :user_id", user_id = session['user_id'])[0]['cash'])
    print(wlt)
    
    return render_template("index.html", ind_ls=ind_ls, len_ls=len(ind_ls), wlt = wlt)

    # return apology("TODO")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    if request.method == "POST":
        
        if not request.form.get("shares"):
            return apology("Amount not entered.")
        
        if not request.form.get("symbol"):
            return apology("Did not enter a symbol.") 
        try:
            num = int(request.form.get("shares"))
        except:
            return apology("-_-")
        if int(request.form.get("shares")) <= 0:
            return apology("Netive")
        
        ls = lookup(request.form.get("symbol"))
        if ls:
            rows = db.execute("SELECT * FROM symbols WHERE symbols = :symbols", symbols=ls['symbol'])
            if len(rows) == 0:
                db.execute("INSERT  INTO symbols( symbols, company ) VALUES( :symbol, :company )",symbol= ls['symbol'], company=ls['name'] )
        else:
            return apology("Not found symbol:(")

        num = request.form.get("shares")
        print(db.execute("SELECT cash FROM users WHERE id = :user_id", user_id = session['user_id'])[0])

        wlt = float(db.execute("SELECT cash FROM users WHERE id = :user_id", user_id = session['user_id'])[0]['cash'])

        if int(num) * ls['price'] > wlt:
            return apology("There are not enough funds.")
        
        am = int(num) * ls['price']

        wlt = wlt - am
        symbol_id =db.execute("SELECT id FROM symbols WHERE symbols = :symbols", symbols=ls['symbol'])[0]['id']

        db.execute("""INSERT  INTO transactions( user_id, symbol_id, number, amount, date, purchase_sale )
                    VALUES( :user_id, :symbol_id, :number, :amount, :date, :purchase_sale)""",
                    user_id = session['user_id'],
                    symbol_id = symbol_id,
                    number = num,
                    amount = am,
                    date = datetime.now(),
                    purchase_sale = "buy"
                    )

        db.execute("UPDATE users SET cash = :cash WHERE id = :user_id" , cash = wlt, user_id = session['user_id'])

        return redirect("/")
    else:
        return render_template("buy.html")


    # return apology("TODO")


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""

    rows = db.execute("SELECT * FROM users WHERE username = :name", name = request.form.get("username"))
    
    return jsonify(len(rows) > 0 and len(request.form.get("username")) > 1)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    if not request.args.get("symbol") or len(request.args.get("symbol")) == 0:
        user_tr = db.execute("SELECT * FROM transactions WHERE user_id = :user_id", user_id = session['user_id'])
    else:
        symbol = db.execute("SELECT id FROM symbols WHERE symbols = :symbol", symbol=request.args.get("symbol"))[0]['id']
        user_tr = db.execute("SELECT * FROM transactions WHERE user_id = :user_id AND symbol_id = :symbol_id",
                                user_id = session['user_id'],
                                symbol_id = symbol
                            )

    ind_ls = []
    
    for tr in user_tr:

        symbol = db.execute("SELECT symbols, company FROM symbols WHERE id = :symbol_id", symbol_id=tr['symbol_id'])[0]

        
        

        
        num = tr['number']
        

        am = tr['amount']


        ind_ls.append({
            'price' : usd(am/num),
            'amount' : usd(am),
            "date" : tr['date'],
            'company' : symbol['company'],
            'symbol' : symbol['symbols'],
            'number' : num,
            'operation': tr['purchase_sale'],
            'id' : tr['id']
        })
    
    if not request.args.get("symbol"):
        return render_template("history.html", len_ls = len(ind_ls), ind_ls=ind_ls, title = "transactions.")
    else:
        return render_template("history.html", len_ls = len(ind_ls), ind_ls=ind_ls, title = f"transactions for {request.args.get('symbol')}.")




@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":


        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                            username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("-_-")
        ls = lookup(request.form.get("symbol"))
        if ls:
            rows = db.execute("SELECT * FROM symbols WHERE symbols = :symbols", symbols=ls['symbol'])
            if len(rows) == 0:
                db.execute("INSERT  INTO symbols( symbols, company ) VALUES( :symbol, :company )",symbol= ls['symbol'], company=ls['name'] )
            ls['price'] = usd(ls['price'])
            return render_template("quoted.html", ls = ls)
        else:
            return apology("Not found symbol:(")
    else:
        return render_template("quote.html")



@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password") or not request.form.get("confirmation"):
            return apology("must provide password", 400)

        if request.form.get("confirmation") != request.form.get("password"):
            return apology("password mismatch", 400)
        
        if len(request.form.get("confirmation")) < 8:
            return apology("password too small", 400)


        rows = db.execute("SELECT * FROM users WHERE username = :name", name = request.form.get("username").lower())

        print(rows)
        if rows:
            return apology("This username is already in use.", 400)


        hash_pass = generate_password_hash(request.form.get("password"))

        db.execute("INSERT INTO users (username, hash) VALUES( :username, :hash_pass )", username=request.form.get("username").lower(), hash_pass=hash_pass)
        

        rows = db.execute("SELECT * FROM users WHERE username = :username",
                            username=request.form.get("username"))


        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        
        if not request.form.get("shares"):
            return apology("Amount not entered.")
        
        try:
            num = int(request.form.get("shares"))
        except:
            return apology("-_-")
        if int(request.form.get("shares")) <= 0:
            return apology("Netive")
        
        if not request.form.get("symbol"):
            return apology("Did not enter a symbol.") 
        rows = db.execute("SELECT * FROM symbols WHERE symbols = :symbols", symbols=request.form.get("symbol").upper())
        if rows:
            apology("You dont have this symbol or symbol not found.")
        print(rows)
        num_buy = db.execute("SELECT SUM(number) FROM transactions WHERE user_id = :user_id AND purchase_sale = 'buy' AND symbol_id = :symbol_id",
                            user_id = session['user_id'],
                            symbol_id = rows[0]['id']
                            )[0]['SUM(number)'] 
        num_sell = db.execute("SELECT SUM(number) FROM transactions WHERE user_id = :user_id AND purchase_sale = 'sell' AND symbol_id = :symbol_id",
                            user_id = session['user_id'],
                            symbol_id = rows[0]['id']
                            )[0]['SUM(number)'] 
        

        if not num_sell:
            num_sell = 0
        num = int(request.form.get("shares"))
        if num_buy - num_sell <  num:
            return apology("There are not enough assets in the account.") 
        
        ls = lookup(request.form.get("symbol"))
        if ls:
            rows = db.execute("SELECT * FROM symbols WHERE symbols = :symbols", symbols=ls['symbol'])
            if len(rows) == 0:
                db.execute("INSERT  INTO symbols( symbols, company ) VALUES( :symbol, :company )",symbol= ls['symbol'], company=ls['name'] )
        else:
            return apology("Not found symbol:(")
        
        
        print(db.execute("SELECT cash FROM users WHERE id = :user_id", user_id = session['user_id'])[0])

        wlt = float(db.execute("SELECT cash FROM users WHERE id = :user_id", user_id = session['user_id'])[0]['cash'])

        am = int(num) * ls['price']

        wlt = wlt + am
        symbol_id =db.execute("SELECT id FROM symbols WHERE symbols = :symbols", symbols=ls['symbol'])[0]['id']

        db.execute("""INSERT  INTO transactions( user_id, symbol_id, number, amount, date, purchase_sale )
                    VALUES( :user_id, :symbol_id, :number, :amount, :date, :purchase_sale)""",
                    user_id = session['user_id'],
                    symbol_id = symbol_id,
                    number = num,
                    amount = am,
                    date = datetime.now(),
                    purchase_sale = "sell"
                    )

        db.execute("UPDATE users SET cash = :cash WHERE id = :user_id" , cash = wlt, user_id = session['user_id'])

        return redirect("/")
    else:
        op = db.execute("SELECT DISTINCT symbols.symbols From symbols JOIN transactions WHERE transactions.user_id = :user_id AND symbols.id = transactions.symbol_id", 
                        user_id = session['user_id']
                        )
        
        return render_template("sell.html", op_list = op)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    
    app.errorhandler(code)(errorhandler)

if __name__ == "__main__":
    app.run(debug=True, port=222)
