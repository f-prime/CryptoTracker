#!/usr/bin/env python

try:
    import urllib.request as urllib
except ImportError:
    import urllib
import json
import argparse
import sys
import os

parser = argparse.ArgumentParser()
parser.add_argument("-i", '--info', help="Get info on a list of currencies separated by space", nargs="+")
parser.add_argument("-c", "--convert", help="Fiat currency to convert price to (Default: USD)")
parser.add_argument("-a", "--add", help="Currency to add to portfolio")
parser.add_argument("--amt", help="Amount of currency to add to portfolio")
parser.add_argument("-rm", "--remove", help="Currency to remove from portfolio")
parser.add_argument("-p", "--portfolio", help="View portfolio", action="store_true")
args = parser.parse_args()

class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class CoinTracker:
    def __init__(self):
        self.currencies_supported = ["AUD", "BRL", "CAD", "CHF", "CLP", "CNY", "CZK", "DKK", "EUR", "GBP", "HKD", "HUF", "IDR", "ILS", "INR", "JPY", "KRW", "MXN", "MYR", "NOK", "NZD", "PHP", "PKR", "PLN", "RUB", "SEK", "SGD", "THB", "TRY", "TWD", "ZAR"]
        self.coin_data_url = "https://api.coinmarketcap.com/v1/ticker/?convert={}"
        self.currency = "USD"

    def parseCommandline(self):
        if args.convert:
            self.changeCurrency(args.convert)
        
        if args.info:
            self.getCoinData(args.info)
        elif args.add:
            amt = args.amt
            self.addToPortfolio(args.add, args.amt)
        elif args.remove:
            self.removeFromPortfolio(args.remove)
        elif args.portfolio:
            self.getPortfolioData()

    def getAPIData(self):
        coin_data = urllib.urlopen(self.coin_data_url.format(self.currency)).read()
        coin_data = json.loads(coin_data)
        return coin_data

    def getCoinData(self, coins):
        coin_data = self.getAPIData()
        table = [
                ["Name", "Price ({})".format(self.currency), "Market Cap", "Percent Change"]
        ]
        for coin in coins:
            for c in coin_data:
                if coin.upper() == c['symbol'] or coin.lower() == c['name'].lower():
                    name = c['symbol']
                    price =  c['price_' + self.currency.lower()]
                    market_cap = c['market_cap_' + self.currency.lower()]
                    percent_change = c['percent_change_1h']
                    if percent_change.startswith("-"):
                        percent_change = percent_change + "%" 
                    else:
                        percent_change = percent_change + "%"
                    table.append([
                        name,
                        price,
                        market_cap,
                        percent_change
                    ])
        self.printTable(table)

    def getPortfolioData(self):
        coin_data = self.getAPIData()
        portfolio = self.getPortfolio()
        table = [
                ["Name", "Price ({})".format(self.currency), "Market Cap", "Percent Change", "Holdings", "Value ({})".format(self.currency)]
        ]
        for coin in portfolio:
            for c in coin_data:
                if c['symbol'] == coin:
                    name = c['symbol']
                    price = c['price_' + self.currency.lower()]
                    market_cap = c['market_cap_' + self.currency.lower()]
                    percent_change = c['percent_change_1h']
                    if percent_change.startswith("-"):
                        percent_change = percent_change + "%"
                    else:
                        percent_change = percent_change + "%"
                    holdings = portfolio[coin]
                    value = float(holdings) * float(price) 
                    value = str(value)
                    price = str(price)
                    table.append([
                        name,
                        price,
                        market_cap,
                        percent_change,
                        holdings,
                        value
                    ])
        self.printTable(table)

        value = []
        for x in table[1:]:
            value.append(float(x[5]))
        value = str(sum(value))
        value = self.printColor(value, colors.WARNING, bold=True)
        print("Total Value: " + value)

    def printTable(self, table):
        max_cols = []
        for columns in range(len(table[0])):
            max_cols.append(max([len(str(x[columns])) for x in table]) + 5)

        for r, row in enumerate(table):
            for i, column in enumerate(row):
                col = str(column)
                spaces = max_cols[i] - len(col) 
                if r > 0:
                    if i == 1:
                        col = self.printColor(col, colors.HEADER, bold=True)
                    elif i == 3:
                        if col.startswith("-"):
                            col = self.printColor(col, colors.FAIL, bold=True)
                        else:
                            col = self.printColor(col, colors.OKGREEN, bold=True)
                    elif i == 4:
                        col = self.printColor(col, colors.OKBLUE, bold=True)
                    elif i == 5:
                        col = self.printColor(col, colors.WARNING, bold=True)
                sys.stdout.write(col + (" " * spaces))
            print("\n")


    def printColor(self, item, color, bold=False):
        return (colors.BOLD if bold else '') + color + item + colors.ENDC

    def addToPortfolio(self, currency, amount):
        apiData = self.getAPIData()
        for data in apiData:
            if currency.upper() == data['symbol'] or currency.lower() == data['name'].lower():
                currency = data['symbol']
                break
        else:
            sys.exit("{} is not supported".format(currency))

        portfolioData = self.getPortfolio()
        portfolioData[currency] = float(amount)
        self.savePortfolio(portfolioData)

    def removeFromPortfolio(self, currency):
        portfolioData = self.getPortfolio()
        if currency in portfolioData:
            del portfolioData[currency.upper()]
            self.savePortfolio(portfolioData)

    def getPortfolio(self):
        if not os.path.exists(os.path.expanduser("~/portfolio.json")):
            return {}
        try:
            return json.load(open(os.path.expanduser("~/portfolio.json")))
        except IOError:
            self.savePortfolio({})
            return {}

    def savePortfolio(self, data):
        json.dump(data, open(os.path.expanduser("~/portfolio.json"), 'w'))

    def changeCurrency(self, currency):
        currency = currency.upper()
        if currency not in self.currencies_supported:
            sys.exit("{} is not currently supported".format(currency))
        self.currency = currency
        
def main():
    ct = CoinTracker()
    ct.parseCommandline()

if __name__ == "__main__":
   main() 
