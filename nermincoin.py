# -*- coding: utf8 -*-

from irc import IRCBot, run_bot

import json
import time
import requests
import re
import random


URL_LIST = []

for currency in ['btc', 'ltc', 'nmc', 'ppc']:
    URL_LIST.append(
        ('https://btc-e.com/api/2/{}_usd/ticker'.format(currency), currency)
    )

for currency in ['trc', 'ftc', 'xpm']:
    URL_LIST.append(
        ('https://btc-e.com/api/2/{}_btc/ticker'.format(currency), currency)
    )  

def get_btcturk():
    btcturk = requests.get("http://btcturk.com").text
    btcturk_price = re.findall('<strong class="bidPrice">(.*?)</strong>', btcturk)[1]
    btcturk_price = re.sub("\s+", "", btcturk_price)[0:-3]

    koinim_price = requests.get("http://koinim.com/ticker/").json()["sell"]

    return "koinim: {0} tl, btcturk: {1} tl".format(koinim_price, btcturk_price).strip()


def _convert_human_readable(coinname, btc_price, price):
    if coinname in ['trc', 'ftc', 'xpm']:       
       return float(btc_price) * float(price)
    return price


def get_qrk(btc_price):
    # qrk to btc
    content = requests.get("https://bter.com/api/1/ticker/qrk_btc").json()
    max_sell = content["last"]

    # btc to usd
    qrk_usd = float(btc_price) * float(max_sell)

    return ", qrk: $" + str(qrk_usd)

class Commands():
  
    BEER_POOL_MAP = {
      "emre": "ALCcH7UhiVqtBjmgGazhSL2DPbD8kJzbMA",
      "selam": "AStUNG9WgcuXrgu6ZNxWfz26b1PsAqQgE3",
      "raistlinthewiz": "AeZmUGwAnZgn785oYTm7K9BqwhW52kVa6E"
    } 

    NEWS_MAP = {
      "btcnews": "bitcoin",
      "ltcnews": "litecoin",
      "qrknews": "quarkcoin"
    }

    def get_currency(self, nick, message, channel):
        message = get_btcturk() + ", "
        btcprice = None
        for index, url in enumerate(URL_LIST):
            currency_data = requests.get(url[0]).json()
            if index == 0:
               btcprice = currency_data["ticker"]["sell"]
            inline_message = '{0}: ${1}, '.format(url[1], _convert_human_readable(url[1], btcprice, currency_data["ticker"]["sell"]))
            message += inline_message

        return message + get_qrk(btcprice)
        
        
    def get_mtgox(self, nick, message, channel):
        data = requests.get("http://data.mtgox.com/api/2/BTCUSD/money/ticker_fast").json()
        return data["data"]["sell"]["display_short"]

    def _news(self, mapname, random_post=None):
        if mapname in self.NEWS_MAP:
            if not random_post:
                random_post = random.randint(0, 5)
            data = requests.get("http://www.reddit.com/r/"+self.NEWS_MAP[mapname]+".json").json()
            latest = data["data"]["children"][random_post]["data"]
            return '{0} ·· {1}'.format(latest["title"], latest["url"])
 
    def get_ltc_news(self, nick, message, channel):
        return self._news("ltcnews")
        
    def get_btc_news(self, nick, message, channel):
        random_post = random.randint(1, 6)
        return self._news("btcnews", random_post=random_post)       
  
        
    def get_qrk_news(self, nick, message, channel):
        return self._news("qrknews")

    def help(self, nick, message, channel):
        return "komutlar: !mtgox, !s, !ltcnews, !btcnews, !qrknews, !beer, !xpm_mining"
        
    def get_beer(self, nick, message, channel):
        for _nick, address in self.BEER_POOL_MAP.iteritems():       
            if nick in _nick:
                 r = requests.get("http://beeeeer.org/user/"+address).text
                 result = re.findall("current balance: (.*?)<br/>", r)
                 
                 return result[0]
            
    def xpm_mining(self, nick, message, channel):      
        XPM_MINING = "beeeeer.org pool'u uzerinden genel bilgi ve miner client: http://www.peercointalk.org/index.php?topic=485.0 " 
        XPM_MINING += "cloud mining: http://www.hiddentao.com/archives/2013/11/24/cloud-primecoin-mining-on-ubuntu-12-04-with-auto-restart"
        
        return XPM_MINING  


class BasicTest(Commands):
  def run_test(self):
    self.get_currency("", "", "")
    self.xpm_mining("", "", "")
    self.get_beer("", "", "")
    self.get_qrk_news("", "", "")
    self.get_btc_news("", "", "")
    self.get_ltc_news("", "", "")
    self.get_mtgox("", "", "")
    
class GreeterBot(IRCBot, Commands):

    def command_patterns(self):
        return (
            ('!s$', self.get_currency),
            ('!mtgox$', self.get_mtgox),
            ('!ltcnews$', self.get_ltc_news),
            ('!btcnews$', self.get_btc_news),
            ('!qrknews$', self.get_qrk_news),
            ('!beer$', self.get_beer),
            ('!xpm_mining', self.xpm_mining),
            ('!help$', self.help)
        )
if __name__ == "__main__":
  try:
    bt = BasicTest()
    bt.run_test()
    run_bot(GreeterBot, 'irc.freenode.net', 6667, 'nermincoin', ['#btcsohbet', '#speedlings', '#bitcoin-tr', '#eksicoin', '#cointurk'])
  except Exception, e:
    print e
