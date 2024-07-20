import mysql.connector

# Клас для підключення до бази даних
# Class for database connection
class MyDB():
    def __init__(self):
        self.myconn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="my-secret-pw",
            database="finance_db"
        )
        self.mycursor = self.myconn.cursor()

    def __del__(self):
        if self.myconn.is_connected():
            self.mycursor.close()
            
            self.myconn.close()
            

        del self.myconn
        del self.mycursor


# Клас для представлення символу (активу) та роботи з ним
# Class to represent a symbol (asset) and interact with it
class Symbol(MyDB):

    def __init__(self, id=None, symbol=None) -> None:
        super().__init__()

        if id is not None:
            self.id = id
            self.symbol, self.company = self.get_inf_for_id()
        elif symbol is not None:
            self.symbol = symbol.upper()
            self.id, self.company = self.get_inf_for_symbol()
        else:
            self.id = None
            self.symbol = None
            self.company = None

    # Отримати інформацію про символ за його ID
    # Get information about the symbol by its ID
    def get_inf_for_id(self):
        self.mycursor.execute("SELECT symbol, company FROM symbols WHERE symbol_id = %s", (self.id,))
        rw = self.mycursor.fetchall()
        if len(rw):
            return [_ for _ in rw[0]]
        return [None, None]

    # Отримати інформацію про символ за його назвою
    # Get information about the symbol by its name
    def get_inf_for_symbol(self):
        self.mycursor.execute("SELECT symbol_id, company FROM symbols WHERE symbol = %s", (self.symbol,))
        rw = self.mycursor.fetchall()
        if len(rw):
            return [_ for _ in rw[0]]
        return [None, None]

    # Додати новий символ в базу даних
    # Add a new symbol to the database
    def new_symbol(self, symbol_name, company):
        self.mycursor.execute("INSERT INTO symbols (symbol, company) VALUES (%s, %s)", (symbol_name, company))
        self.myconn.commit()

        self.symbol = symbol_name
        self.id, self.company = self.get_inf_for_symbol()
        return self

# Клас для роботи з транзакціями користувача
# Class to handle user transactions
class Transaction(MyDB):
    def __init__(self, user_id) -> None:
        super().__init__()
        self.user_id = user_id
        self.transactions = self.get_inf()

    # Отримати інформацію про всі транзакції користувача
    # Get information about all user transactions
    def get_inf(self):
        self.mycursor.execute("SELECT id, symbol_id, quantity, price, transaction_date, transaction_type FROM transactions WHERE user_id = %s", (self.user_id,))
        trs = self.mycursor.fetchall()
        res = []
        for tr in trs:
            res.append(
                {
                    'id': tr[0],
                    'symbol': Symbol(id=tr[1]),
                    'quantity': float(tr[2]),
                    'price': float(tr[3]),
                    'transaction_date': tr[4],
                    'transaction_type': tr[5]
                }
            )
        return res

    # Отримати транзакції за конкретним символом
    # Get transactions for a specific symbol
    def get_trs_by_symbol(self, symbol_name):
        res = []
        for tr in self.transactions:
            if tr['symbol'].symbol == symbol_name:
                res.append(tr)
        return res

    # Додати нову транзакцію
    # Add a new transaction
    def new_transaction(self, symbol, quantity, price, transaction_type):
        self.mycursor.execute("""INSERT INTO transactions(user_id, symbol_id, quantity, price, transaction_type)
                                VALUES (%s, %s, %s, %s, %s)""",
                                (self.user_id, symbol.id, quantity, price, transaction_type))
        self.myconn.commit()
        self.transactions = self.get_inf()

# Клас для управління активами користувача
# Class to manage user assets
class UserAssets(MyDB):
    def __init__(self, user_id) -> None:
        super().__init__()
        self.user_id = user_id
        self.assets = self.get_inf()

    # Отримати інформацію про активи користувача
    # Get information about user assets
    def get_inf(self):
        self.mycursor.execute("SELECT symbol_id, quantity FROM UserAssets WHERE user_id = %s", (self.user_id,))
        assets = [_ for _ in self.mycursor.fetchall()]
        res = {}
        for asset in assets:
            symbol_id = asset[0]
            symbol = Symbol(id=symbol_id)
            res[symbol.symbol] = {
                "quantity": asset[1],
                "symbol": symbol
            }
        return res

    # Додати символ до активів користувача
    # Add a symbol to user assets
    def add_symb(self, symbol, qnt):
        if symbol.symbol in self.assets:
            self.assets[symbol.symbol]['quantity'] += qnt
            self.assets[symbol.symbol]['symbol'] = symbol
            self.mycursor.execute("UPDATE UserAssets SET quantity = %s WHERE user_id = %s AND symbol_id = %s", 
                                (self.assets[symbol.symbol]['quantity'], self.user_id, symbol.id))
            self.myconn.commit()
        else:
            self.assets[symbol.symbol] = {
                'quantity': qnt,
                'symbol': symbol
            }
            self.mycursor.execute("INSERT INTO UserAssets (user_id, symbol_id, quantity) VALUES (%s, %s, %s)", 
                                (self.user_id, symbol.id, qnt))
            self.myconn.commit()

    # Видалити символ з активів користувача
    # Remove a symbol from user assets
    def pop_symb(self, symbol, qnt):
        if symbol.symbol in self.assets:
            if self.assets[symbol.symbol]['quantity'] < qnt:
                return False
            elif self.assets[symbol.symbol]['quantity'] == qnt:
                self.mycursor.execute("DELETE FROM UserAssets WHERE user_id = %s AND symbol_id = %s", 
                                    (self.user_id, symbol.id))
                self.myconn.commit()
                del self.assets[symbol.symbol]
                return True
            self.assets[symbol.symbol]['quantity'] -= qnt
            self.assets[symbol.symbol]['symbol'] = symbol
            self.mycursor.execute("UPDATE UserAssets SET quantity = %s WHERE user_id = %s AND symbol_id = %s", 
                                (self.assets[symbol.symbol]['quantity'], self.user_id, symbol.id))
            self.myconn.commit()
            return True
        else:
            return False

# Клас для управління інформацією про користувача
# Class to manage user information
class User(MyDB):

    def __init__(self, username=None, id=None) -> None:
        super().__init__()
        self.cash = None
        self.id = id
        self.username = username
        if username is not None:
            self.username = username
            self.id, self.cash, self.pass_hash, self.current_balance = self.get_inf_for_username()
        elif id is not None:
            self.id = id
            self.username, self.cash, self.pass_hash, self.current_balance = self.get_inf_for_id()
        if self.cash is not None:
            self.cash = float(self.cash)
        self.asset = UserAssets(self.id)
        self.trs = Transaction(user_id=self.id)

    # Отримати інформацію про користувача за його ID
    # Get user information by ID
    def get_inf_for_id(self):
        self.mycursor.execute("SELECT username, cash, hash, current_balance FROM users WHERE user_id = %s", (self.id,))
        col = self.mycursor.fetchall()
        if len(col):
            return tuple([_ for _ in col[0]])
        return [None, None, None, None]

    # Отримати інформацію про користувача за його ім'ям
    # Get user information by username
    def get_inf_for_username(self):
        self.mycursor.execute("SELECT user_id, cash, hash, current_balance FROM users WHERE username = %s", (self.username,))
        col = self.mycursor.fetchall()
        if len(col):
            return tuple([_ for _ in col[0]])
        return [None, None, None, None]

    # Функція покупки символів користувачем
    # Function for buying symbols by the user
    def buy(self, symbol, qnt, price):
        if price * qnt > self.cash:
            return False
        self.cash -= price * qnt
        self.mycursor.execute("UPDATE users SET cash = %s WHERE user_id = %s", (self.cash, self.id))
        self.myconn.commit()
        self.asset.add_symb(Symbol(symbol=symbol), qnt=qnt)
        self.trs.new_transaction(symbol=Symbol(symbol=symbol), quantity=qnt, price=price, transaction_type="BUY")
        return True

    # Функція продажу символів користувачем
    # Function for selling symbols by the user
    def sell(self, symbol, qnt, price):
        res = self.asset.pop_symb(Symbol(symbol=symbol), qnt=qnt)
        if res:
            self.trs.new_transaction(symbol=Symbol(symbol=symbol), quantity=qnt, price=price, transaction_type="SELL")
            self.cash += price * qnt
            self.mycursor.execute("UPDATE users SET cash = %s WHERE user_id = %s", (self.cash, self.id))
            self.myconn.commit()
            return True
        return False

    # Додавання нового користувача
    # Add a new user
    def new_user(self, username, hash):
        self.mycursor.execute("INSERT INTO users (username, hash) VALUES(%s, %s)", (username, hash))
        self.myconn.commit()
        self.username = username
        self.id, self.cash, self.pass_hash, self.current_balance = self.get_inf_for_username()
        self.cash = float(self.cash)
