import os
import signal
import mysql.connector
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from helpers import apology, login_required, lookup, usd
from conn_db import check_create_db
from docker_db import start_db, stop_db
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

myconn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="my-secret-pw",
    database="finance_db"
)

mycursor = myconn.cursor(buffered=True)


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    
    mycursor.execute("SELECT * FROM transactions WHERE user_id = %s", (session['user_id'], ))
    user_tr = mycursor.fetchall()
    print(user_tr)
    ind_ls = []
    symb_ind = dict()
    count_symb = 0
    for tr in user_tr:

        mycursor.execute("SELECT symbols FROM symbols WHERE id = %s", ( tr[2], ) )
        print(tr[0])
        
        symbol = mycursor.fetchall()[0][0]
        print(symbol)
        if not symbol in symb_ind:
            
            
            
            
            
            new_inf = lookup(symbol)    
            mycursor.execute("SELECT SUM(number) FROM transactions WHERE user_id = %s AND purchase_sale = 'buy' AND symbol_id = %s",
                            (session['user_id'],
                            tr[2] )
                            )
            num_buy = mycursor.fetchall()[0][0]
            mycursor.execute("SELECT SUM(number) FROM transactions WHERE user_id = %s AND purchase_sale = 'sell' AND symbol_id = %s",
                                (session['user_id'],
                                tr[2] )
                                )
            num_sell = mycursor.fetchall()[0][0]
            if not num_sell:
                num_sell = 0

            num = num_buy - num_sell

            
            mycursor.execute("SELECT SUM(amount) FROM transactions WHERE symbol_id = %s AND user_id = %s ",
                            (tr[2],
                            session['user_id'] )
                            )
            am = mycursor.fetchall()[0][0]
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
            
    mycursor.execute("SELECT cash FROM users WHERE id = %s", ( session['user_id'], ))
    wlt = usd(mycursor.fetchall()[0][0])
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
            mycursor.execute("SELECT * FROM symbols WHERE symbols = %s", (ls['symbol'], ))
            rows = mycursor.fetchall()
            if len(rows) == 0:
                mycursor.execute("INSERT  INTO symbols( symbols, company ) VALUES( %s, %s )",( ls['symbol'], ls['name'] ) )
                myconn.commit()
        else:
            return apology("Not found symbol:(")

        num = request.form.get("shares")
        mycursor.execute("SELECT cash FROM users WHERE id = %s", ( session['user_id'], ))
        wlt = float(mycursor.fetchall()[0][0])

        if int(num) * ls['price'] > wlt:
            return apology("There are not enough funds.")
        
        am = int(num) * ls['price']

        wlt = wlt - am
        mycursor.execute("SELECT id FROM symbols WHERE symbols = %s", ( ls['symbol'], ))
        symbol_id = mycursor.fetchall()[0][0]

        mycursor.execute("""INSERT  INTO transactions( user_id, symbol_id, number, amount, date, purchase_sale )
                    VALUES( %s, %s, %s, %s, %s, %s)""",
                    (session['user_id'],
                    symbol_id,
                    num,
                    am,
                    datetime.now(),
                    "buy"
                    )
                    )
        myconn.commit()

        mycursor.execute("UPDATE users SET cash = %s WHERE id = %s" ,( wlt, session['user_id']))
        myconn.commit()
        return redirect("/")
    else:
        return render_template("buy.html")


    # return apology("TODO")


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""

    mycursor.execute("SELECT * FROM users WHERE username = %s", (request.form.get("username"), ))
    rows = mycursor.fetchall()
    return jsonify(len(rows) > 0 and len(request.form.get("username")) > 1)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    if not request.args.get("symbol") or len(request.args.get("symbol")) == 0:
        mycursor.execute("SELECT * FROM transactions WHERE user_id = %s", (session['user_id'],) )
        user_tr = mycursor.fetchall()
    else:
        mycursor.execute("SELECT id FROM symbols WHERE symbols = %s", (request.args.get("symbol"), ))
        symbol = mycursor.fetchall()[0][0]
        mycursor.execute("SELECT * FROM transactions WHERE user_id = %s AND symbol_id = %s",
                                (session['user_id'],
                                symbol)
                            )
        user_tr = mycursor.fetchall()
    ind_ls = []
    
    for tr in user_tr:

        mycursor.execute("SELECT symbols, company FROM symbols WHERE id = %s", (tr[2],))
        symbol = mycursor.fetchall()[0]
        
        print(symbol)

        
        num = tr[3]
        

        am = tr[4]


        ind_ls.append({
            'price' : usd(am/num),
            'amount' : usd(am),
            "date" : tr[-2],
            'company' : symbol[1],
            'symbol' : symbol[0],
            'number' : num,
            'operation': tr[-1],
            'id' : tr[0]
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
        mycursor.execute("SELECT * FROM users WHERE username = %s",
                            ( request.form.get("username"), ))
        rows = mycursor.fetchall()
        # Ensure username exists and password is correct
        print(rows)
        if len(rows) == 0 or not check_password_hash(rows[0][2], request.form.get("password")):
            return apology("invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0][0]

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
            mycursor.execute("SELECT * FROM symbols WHERE symbols = %s", (ls['symbol'], ))
            rows = mycursor.fetchall()
            if len(rows) == 0:
                mycursor.execute("INSERT  INTO symbols( symbols, company ) VALUES( %s, %s )",( ls['symbol'], ls['name'] ))
                myconn.commit()
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


        mycursor.execute("SELECT * FROM users WHERE username = %s", (request.form.get("username").lower(), ))
        rows = mycursor.fetchall()
        print(rows)
        if rows:
            return apology("This username is already in use.", 400)


        hash_pass = generate_password_hash(request.form.get("password"))

        mycursor.execute("INSERT INTO users (username, hash) VALUES( %s, %s )", (request.form.get("username").lower(), hash_pass) )
        myconn.commit()

        mycursor.execute("SELECT * FROM users WHERE username = %s",
                            ( request.form.get("username"), ))
        rows = mycursor.fetchall()
        print(rows)
        # Remember which user has logged in
        session["user_id"] = rows[0][0]

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
        mycursor.execute("SELECT * FROM symbols WHERE symbols = %s", ( request.form.get("symbol").upper(),) )
        rows = mycursor.fetchall()
        if rows:
            apology("You dont have this symbol or symbol not found.")
        print(rows)
        mycursor.execute("SELECT SUM(number) FROM transactions WHERE user_id = %s AND purchase_sale = 'buy' AND symbol_id = %s",
                            ( session['user_id'],
                            rows[0][0])
                            )
        num_buy = mycursor.fetchall()[0][0]
        mycursor.execute("SELECT SUM(number) FROM transactions WHERE user_id = %s AND purchase_sale = 'sell' AND symbol_id = %s",
                            ( session['user_id'],
                            rows[0][0])
                            )
        num_sell = mycursor.fetchall()[0][0]
        

        if not num_sell:
            num_sell = 0
        num = int(request.form.get("shares"))
        if num_buy - num_sell <  num:
            return apology("There are not enough assets in the account.") 
        
        ls = lookup(request.form.get("symbol"))
        if ls:
            mycursor.execute("SELECT * FROM symbols WHERE symbols = %s", ( ls['symbol'], ))
            rows = mycursor.fetchall()
            if len(rows) == 0:
                mycursor.execute("INSERT  INTO symbols( symbols, company ) VALUES( %s, %s )",( ls['symbol'], ls['name'])  )
                myconn.commit()
        else:
            return apology("Not found symbol:(")
        
        
        # print(mycursor.execute("SELECT cash FROM users WHERE id = %s", ( session['user_id'], ))[0])
        mycursor.execute("SELECT cash FROM users WHERE id = %s", ( session['user_id'], ))
        wlt = float(mycursor.fetchall()[0][0])

        am = int(num) * ls['price']

        wlt = wlt + am
        mycursor.execute("SELECT id FROM symbols WHERE symbols = %s", ( ls['symbol'], ))
        symbol_id = mycursor.fetchall()[0][0]
        mycursor.execute("""INSERT  INTO transactions( user_id, symbol_id, number, amount, date, purchase_sale )
                    VALUES( %s, %s, %s, %s, %s, %s)""",
                    (session['user_id'],
                    symbol_id,
                    num,
                    am,
                    datetime.now(),
                    "sell"
                    )
                    )
        myconn.commit()

        mycursor.execute("UPDATE users SET cash = %s WHERE id = %s" , ( wlt, session['user_id']))
        myconn.commit()
        return redirect("/")
    else:
        mycursor.execute("SELECT DISTINCT symbols.symbols From symbols JOIN transactions WHERE transactions.user_id = %s AND symbols.id = transactions.symbol_id", 
                        ( session['user_id'], )
                        )
        op = mycursor.fetchall()
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

    container_id = start_db()
    check_create_db()
    
    app.run(debug=True)
    
    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
