import mysql.connector


# class MyDBMeta(type):

#     _instances = {}

#     def __call__(cls, *args, **kwargs):
#         if cls not in cls._instances:
#             instance = super().__call__(*args, **kwargs)
#             cls._instances[cls] = instance
#         return cls._instances[cls]


class MyDB():
    def __init__(self):
        self.myconn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="my-secret-pw",
        database="finance_db"
        )
        self.mycursor = self.myconn.cursor(buffered=True)

class Symbol(MyDB):

    def __init__(self, id = None, symbol = None) -> None:
        super().__init__()

        
        print(symbol,"ZZZZZZZZZZZZZZZZz")
        if id != None:
            self.id = id
            self.symbol, self.company = self.get_inf_for_id()
        elif symbol != None:
            self.symbol = symbol.upper()
            self.id, self.company = self.get_inf_for_symbol()
        else:
            self.id = None
            self.symbol = None
            self.company = None

    def get_inf_for_id(self):
        
        self.mycursor.execute("SELECT symbol, company FROM symbols WHERE symbol_id = %s", ( self.id, ) )
        rw = self.mycursor.fetchall()
        if len(rw):
            return [ _ for _ in rw[0] ]
        return [None, None]
    def get_inf_for_symbol(self):
        
        self.mycursor.execute("SELECT symbol_id, company FROM symbols WHERE symbol = %s", ( self.symbol, ) )
        rw = self.mycursor.fetchall()
        if len(rw):
            return [ _ for _ in rw[0] ]
        return [None, None]

    def new_symbol(self, symbol_name, company):

        self.mycursor.execute("INSERT INTO symbols (symbol, company) VALUES ( %s, %s)", (symbol_name, company))
        self.myconn.commit()
        
        self.symbol = symbol_name
        self.id, self.company = self.get_inf_for_symbol()
        return self
    
class transactions:
    def __init__(self, user) -> None:
        self.user = user
        self

class UserAssets(MyDB):

    def __init__(self, user_id) -> None:
        super().__init__()

        
        self.user_id = user_id

        self.assets = self.get_inf()

    def get_inf(self):
        self.mycursor.execute("SELECT symbol_id, quantity FROM UserAssets WHERE user_id = %s", ( self.user_id, ) )


        assets = [ _ for _ in self.mycursor.fetchall() ]
        res = {}
        for asset in assets:
            symbol_id = asset[0]
            
            symbol = Symbol(id=symbol_id)
            print(asset)
            res[symbol.symbol] = {
                "quantity": asset[1],
                "symbol": symbol
            }
        return res

    def add_symb(self, symbol, qnt):
        

        if symbol.symbol in self.assets:
            self.assets[symbol.symbol]['quantity'] += qnt
            self.assets[symbol.symbol]['symbol'] = symbol
            self.mycursor.execute("UPDATE  UserAssets SET quantity = %s  WHERE user_id = %s AND symbol_id = %s", (self.assets[symbol.symbol]['quantity'], self.user_id, symbol.id) )

            self.myconn.commit()
        else:
            self.assets[symbol.symbol] = {
                'quantity': qnt,
                'symbol': symbol
            }

            self.mycursor.execute("INSERT INTO UserAssets (user_id, SYMBOL_id, quantity) VALUES ( %s, %s, %s )", (self.user_id, symbol.id, qnt) )

            self.myconn.commit()
    
    def pop_symb(self, symbol, qnt):
        
        
        if symbol.symbol in self.assets:

            if self.assets[symbol.symbol]['quantity'] < qnt:
                return False
            elif self.assets[symbol.symbol]['quantity'] == qnt:
                self.mycursor.execute("DELETE FROM UserAssets WHERE user_id = %s AND symbol_id = %s", (self.user_id, symbol.id) )
                self.myconn.commit()
                del self.assets[symbol.symbol]
                return True

            self.myconn.commit()
            self.assets[symbol.symbol]['quantity'] -= qnt
            self.assets[symbol.symbol]['symbol'] = symbol
            self.mycursor.execute("UPDATE  UserAssets SET quantity = %s  WHERE user_id = %s AND symbol_id = %s", (self.assets[symbol.symbol]['quantity'], self.user_id, symbol.id) )

            self.myconn.commit()
            return True
        else:
            return False



    
    
class User(MyDB):
    
    def __init__(self, username = None, id = None) -> None:
        super().__init__()
        
        if username != None:
            self.username = username
            self.id, self.cash, self.pass_hash, self.current_balance = self.get_inf_for_username()
        elif id != None:
            self.id = id
            self.username, self.cash, self.pass_hash, self.current_balance = self.get_inf_for_id()
        if self.cash != None:
            self.cash = float(self.cash)
        self.asset = UserAssets(self.id)
    
    def get_inf_for_id(self):
        self.mycursor.execute("SELECT username, cash, hash, current_balance FROM users WHERE user_id = %s", ( self.id, ) )
        col = self.mycursor.fetchall()

        print(col)
        if len(col):
            return tuple([ _ for _ in col[0] ])
        
        return [None, None, None, None]
    
    def get_inf_for_username(self):
        self.mycursor.execute("SELECT user_id, cash, hash, current_balance FROM users WHERE username = %s", ( self.username, ) )
        col = self.mycursor.fetchall()

        print(col)
        if len(col):
            return tuple([ _ for _ in col[0] ])
        
        return [None, None, None, None]
    
    def buy(self, symbol, qnt, price):
        
        if price * qnt > self.cash:
            return False
        
        self.cash -= price * qnt
        self.mycursor.execute("UPDATE  users SET cash = %s  WHERE user_id = %s", (self.cash, self.id) )

        self.myconn.commit()
        return self.asset.add_symb(Symbol(symbol=symbol), qnt=qnt)
    
    def sell(self, symbol, qnt, price):
        
        if self.asset.pop_symb(Symbol(symbol=symbol), qnt=qnt):
            self.cash += price * qnt
            self.mycursor.execute("UPDATE  users SET cash = %s  WHERE user_id = %s", (self.cash, self.id) )
        
            self.myconn.commit()
            return True
        return False
    
    def new_user(self, username, hash):

        self.mycursor.execute("INSERT INTO users (username, hash) VALUES( %s, %s )", (username, hash) )
        self.myconn.commit()

        self.username = username
        self.id, self.cash, self.pass_hash, self.current_balance = self.get_inf_for_username()
        self.cash = float(self.cash)


if __name__ == "__main__":
    x = User(username="kek")
    y = Symbol(symbol= "ZZZ")

    print(y.id, y.company, y.symbol)
    # x.select_inf("users")

    # print(x.id, x.cash, x.username, x.asset.assets)
    # x.new_user("kek", "scrypt:32768:8:1$a3QLEJq1k39JltHB$fa4a58365759c479720ea21897b37c390064140e115a7d1d66ffcd2cdbc1dd3a4b8aead0ff2dccd298501eb7bc45a82db794d49e79a51d48cbc008344031ed74")
    # print(x.id, x.cash, x.username, x.asset.assets)

    # x = UserAssets(1)
    # print(x.assets)
