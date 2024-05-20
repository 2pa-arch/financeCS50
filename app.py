import os
import signal
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from helpers import apology, login_required, lookup, usd
from conn_db import check_create_db
from use_db import User, Symbol
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



@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    user = User(id=session['user_id'])
    ind_ls = []
    for tr in user.asset.assets:
        
        symbol = user.asset.assets[tr]['symbol']
        new_inf = lookup(symbol.symbol)
        num = user.asset.assets[tr]['quantity']
        new_am = num * new_inf['price']
        ind_ls.append({
                    'price' : usd(new_inf['price']),
                    "new_amount" : usd(new_am),
                    'company' : new_inf['name'],
                    'symbol' : symbol.symbol,
                    'quantity' : num
                })
        
                
            
    
    wlt = usd(user.cash)
    
    
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
        symbol = Symbol(request.form.get("symbol"))
        if ls:
            
            if symbol.company == None:
                symbol.new_symbol(symbol_name=ls['symbol'], company=ls['name'])

        else:
            return apology("Not found symbol:(")
        
        user = User(id = session['user_id'])
        num = int(request.form.get("shares"))
        

        if num * ls['price'] > user.cash:
            return apology("There are not enough funds.")


        user.buy(symbol=symbol.symbol, qnt=num, price=ls['price'])
        return redirect("/")
    else:
        return render_template("buy.html")


    # return apology("TODO")


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""

    user = User(username=request.form.get("username"))
    return jsonify(user.cash != None)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_tr = []
    user = User(id=session['user_id'])
    if not request.args.get("symbol") or len(request.args.get("symbol")) == 0:
        user_tr = user.trs.transactions
    else:
        user_tr = user.trs.get_trs_by_symbol(request.args.get("symbol"))
    ind_ls = []
    
    for tr in user_tr:
        symbol = tr['symbol']        
        qnt = tr['quantity']
        

        am = tr['price'] * qnt


        ind_ls.append({
            'price' : usd(tr['price']),
            'amount' : usd(am),
            "date" : tr['transaction_date'],
            'company' : symbol.company,
            'symbol' : symbol.symbol,
            'quantity' : int(qnt),
            'operation': tr['transaction_type'],
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
        user = User(username=request.form.get("username").lower())
        # Ensure username exists and password is correct
        
        if user.cash == None or not check_password_hash(user.pass_hash, request.form.get("password")):
            return apology("invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = user.id

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
            sym = request.form.get("symbol")
            symbol = Symbol(symbol=sym)
            
            print(symbol.company, symbol.symbol, request.form.get("symbol"))
            if symbol.company == None:
                print("DAFDWEWFWEFWWFWEF")
                symbol.new_symbol(symbol_name=ls['symbol'], company=ls['name'])
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


        user = User(username=request.form.get("username").lower())

        if user.cash != None:
            return apology("This username is already in use.", 400)


        hash_pass = generate_password_hash(request.form.get("password"))

        user.new_user(username=request.form.get("username").lower(), hash=hash_pass)

        
        # Remember which user has logged in
        session["user_id"] = user.id

        # Redirect user to home page
        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    user = User(id=session['user_id'])
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
        
        symbol = Symbol(symbol=request.form.get("symbol").upper())
        
        if symbol.company == None:
            apology("You dont have this symbol or symbol not found.")
        
        
        num = int(request.form.get("shares"))
        ls = lookup(request.form.get("symbol"))

        
        
        if ls:
            sym = request.form.get("symbol")
            symbol = Symbol(symbol=sym)
            pr = ls['price']
            print(symbol.company, symbol.symbol, request.form.get("symbol"))
            if symbol.company == None:
                print("DAFDWEWFWEFWWFWEF")
                symbol.new_symbol(symbol_name=ls['symbol'], company=ls['name'])
            ls['price'] = usd(ls['price'])
        else:
            return apology("Not found symbol:(")
        
        if not user.sell(symbol=symbol.symbol, qnt=num,price=pr):
            return apology("There are not enough assets in the account.") 
                
        return redirect("/")
    else:
        op = [ sym for sym in user.asset.assets ]

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
    
    check_create_db()
    
    app.run(debug=True)
    
