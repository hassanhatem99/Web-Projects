import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user_id = session["user_id"]
    stocks = db.execute("SELECT symbol, name, price, SUM(shares) FROM transactions WHERE user_id = ? GROUP BY symbol", user_id)
    cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]
    total = cash
    for stock in stocks:
        total += stock["price"] * stock["SUM(shares)"]

    return render_template("index.html", stocks=stocks, cash=usd(cash), total=usd(total), usd=usd)


@app.route("/account")
@login_required
def account():
    return render_template("account.html")


@app.route("/change_pass", methods=["GET", "POST"])
@login_required
def change_pass():
    user_id = session["user_id"]
    if request.method == "POST":
        old_pass = request.form.get("old_pass")
        new_pass = request.form.get("new_pass")
        confirmation = request.form.get("confirmation")
        rows = db.execute("SELECT * FROM users WHERE id = ?", user_id)
        if not old_pass:
            return apology("must provide old password", 403)
        if not new_pass:
            return apology("must provide new password", 403)
        if not confirmation:
            return apology("must confirm password", 403)

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], old_pass):
            return apology("Old password is incorrect")
        if new_pass == old_pass:
            return apology("Your new password must be different from the old one")
        if new_pass != confirmation:
            return apology("Password and confirmation don't match")

        hash = generate_password_hash(new_pass)
        db.execute("UPDATE users SET (hash) = ? WHERE id = ?", hash, user_id)
        return redirect('/login')
    else:
        return render_template("change_pass.html")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol").upper()
        if not symbol:
            return apology("Please Enter Stock Symbol!")

        item = lookup(symbol)
        if not item:
            return apology("Invalid Stock Symbol!")

        shares = request.form.get("shares")
        if not shares:
            return apology("Please enter number of shares!")

        try:
            shares = float(shares)
            if shares <= 0:
                return apology("Please enter a positive number!")
            elif shares != int(shares):
                return apology("Please enter an integer!")
            else:
                shares = int(shares)
        except:
            return apology("Please enter a number!")

        user_id = session["user_id"]
        cash = float(db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"])
        item_name = item["name"]
        price = float(item["price"])
        total = price * shares

        if cash < total:
            return apology("Sorry, You're not rich enough!")
        else:
            cash -= total
            db.execute("UPDATE users SET cash = ? WHERE id = ?", cash, user_id)
            db.execute("INSERT INTO transactions (user_id, name, shares, price, type, symbol) VALUES(?, ?, ?, ?, ?, ?)",
                       user_id, item_name, shares, price, "buy", symbol)

        total = usd(total)

        return redirect("/")
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_id = session["user_id"]
    history_list = db.execute("SELECT * FROM transactions WHERE user_id = ?", user_id)
    symbol = db.execute("SELECT symbol FROM transactions WHERE user_id = ?", user_id)
    shares = db.execute("SELECT shares FROM transactions WHERE user_id = ?", user_id)
    price = db.execute("SELECT price FROM transactions WHERE user_id = ?", user_id)
    time = db.execute("SELECT time FROM transactions WHERE user_id = ?", user_id)

    history_list.reverse()
    return render_template("history.html", history_list=history_list, symbol=symbol, shares=shares, price=price, time=time)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

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
    """Get stock quote."""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("Please Enter Stock Symbol!")
        item = lookup(symbol)
        if not item:
            return apology("Invalid Stock Symbol!")
        price = usd(item['price'])
        return render_template("quoted.html", item=item, price=price)

    else:
        return render_template("quote.html")


@app.route("/quoted", methods=["GET", "POST"])
@login_required
def quoted():
    """quoted"""
    return render_template("quoted.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')
        # Ensure username, password, confirmation were submitted
        if not username:
            return apology("must provide username")
        if not password:
            return apology("must provide password")
        if not confirmation:
            return apology("must confirm password")
        if password != confirmation:
            return apology("passwords don't match")

        # Hash password
        hash = generate_password_hash(password)
        try:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)
            return redirect('/')
        except:
            return apology("username already exists")

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    user_id = session["user_id"]
    if request.method == "POST":
        symbol = request.form.get("symbol").upper()
        if not symbol:
            return apology("Please Enter Stock Symbol!")

        shares_sell = request.form.get("shares")
        if not shares_sell:
            return apology("Please enter number of shares!")
        try:
            shares_sell = float(shares_sell)
            if shares_sell <= 0:
                return apology("Please enter a positive number!")
            elif shares_sell != int(shares_sell):
                return apology("Please enter an integer!")
            else:
                shares_sell = int(shares_sell)
        except:
            return apology("Please enter a number!")

        shares_bought = db.execute(
            "SELECT SUM(shares) FROM transactions WHERE user_id = ? AND symbol = ? AND type = ?", user_id, symbol, "buy")[0]["SUM(shares)"]
        shares_sold = db.execute(
            "SELECT SUM(shares) FROM transactions WHERE user_id = ? AND symbol = ? AND type = ?", user_id, symbol, "sell")[0]["SUM(shares)"]
        if not shares_sold:
            shares_have = shares_bought
        else:
            shares_have = shares_bought - shares_sold

        item = lookup(symbol)
        item_name = item["name"]
        price = float(item["price"])
        total = price * shares_have
        if shares_have < shares_sell:
            return apology(f"Sorry, you own less than {shares_sell} shares")

        cash_before = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]
        cash_after = cash_before + price * shares_sell
        shares_have -= shares_sell
        db.execute("UPDATE users SET cash = ? WHERE id = ?", cash_after, user_id)
        db.execute("INSERT INTO transactions (user_id, name, shares, price, type, symbol) VALUES(?, ?, ?, ?, ?, ?)",
                   user_id, item_name, -shares_sell, price, "sell", symbol)

        total = usd(total)

        return redirect("/")
    else:
        symbols = db.execute("SELECT symbol FROM transactions WHERE user_id = ? GROUP BY symbol", user_id)
        return render_template("sell.html", symbols=symbols)


