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
        print("Name\tPrice ({0})\tMarket Cap ({0})\tPercent Change\n".format(self.currency))
        for coin in coins:
            for c in coin_data:
                if coin.upper() == c['symbol'] or coin.lower() == c['name'].lower():
                    name = c['symbol']
                    price = c['price_' + self.currency.lower()]
                    market_cap = c['market_cap_' + self.currency.lower()]
                    percent_change = c['percent_change_1h']

                    print("{}\t{}\t\t{}\t\t{}%\n".format(name, price, market_cap, percent_change))

    def getPortfolioData(self):
        coin_data = self.getAPIData()
        portfolio = self.getPortfolio()
        print("Name\tPrice ({0})\tMarket Cap ({0})\tPercent Change\tHoldings\tValue ({0})\n".format(self.currency))
        for coin in portfolio:
            for c in coin_data:
                if c['symbol'] == coin:
                    name = c['symbol']
                    price = c['price_' + self.currency.lower()]
                    market_cap = c['market_cap_' + self.currency.lower()]
                    percent_change = c['percent_change_1h']
                    holdings = portfolio[coin]
                    value = float(holdings) * float(price)
                    print("{}\t{}\t\t{}\t\t{}%\t\t{}\t\t{}\n".format(name, price, market_cap, percent_change, holdings, value))


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
            del portfolioData[currency]
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
        
if __name__ == "__main__":
    ct = CoinTracker()
    ct.parseCommandline()
