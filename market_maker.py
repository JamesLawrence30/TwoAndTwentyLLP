import sys
import time
import credentials
import numpy as np
import datetime as dt
import shift


def trafficLight(rightNow, dayStart, wait):

    if dayStart > rightNow:
        print("Wait till market open")
        time.sleep(wait)
        print(dt.datetime.now())
        trafficLight(dt.datetime.now(), dayStart, wait)
    else:
        print("Begin Trading")
        return


def closePositions(trader: shift.Trader, ticker, lastTrade):

    # Cancel pending orders
    print("Waiting list size: " + str(trader.get_waiting_list_size()) + " , Canceling all pending orders...")
    trader.cancel_all_pending_orders()
    print("Waiting list size: " + str(trader.get_waiting_list_size()))
    print("All pending orders cancelled") # Cancel outstanding open orders before entering closing orders


    # Close / Cover all open positions
    """
    Either sell at market or at best bid w/ volume required
    """
    """
    if lastTrade is 'B': # Close out long position
        aapl_market_sell = shift.Order(shift.Order.Type.MARKET_SELL, ticker, 1)
        trader.submit_order(aapl_market_sell)
    else: # Cover short position
        aapl_market_buy = shift.Order(shift.Order.Type.MARKET_BUY, ticker, 1)
        trader.submit_order(aapl_market_buy)
    """
    print("**TODO** All closing orders submitted")

    return


def moneyMaker(trader: shift.Trader, ticker, dayEnd, lag):

    # Datetime beginning trading
    rightNow = dt.datetime.now()

    # FIFO queue initialized
    priceQueue = []

    currentDirection = 0
    signal = 'S'
    count = 0

    # While the time is before end of day...
    while(dayEnd > rightNow):
        # Pause and wait for change in prices
        #time.sleep(lag)
        print("Total P/L:",trader.get_portfolio_summary().get_total_realized_pl())
        """
        Make Trades Here:
        """
        """
        if len(priceQueue) > 2: # Queue is full
            firstDeriv = np.gradient(priceQueue, 1) # Find rate of change of prices

            # Prices switch from decreasing to increasing = buy  [buy @ local minima]
            if firstDeriv[2] > 0 and signal is 'S':
                #trader.cancel_all_pending_orders() # Make sure we have buying power
                limit_buy = shift.Order(shift.Order.Type.LIMIT_BUY, ticker, 10, trader.get_best_price(ticker).get_bid_price())
                trader.submit_order(limit_buy)
                print("buy @", trader.get_last_price(ticker))
                signal = 'B'
            # Prices switch from increasing to decreasing = sell  [sell @ local maxima]
            elif firstDeriv[2] < 0 and signal is 'B':
                #trader.cancel_all_pending_orders() # Make sure we have buying power
                limit_buy = shift.Order(shift.Order.Type.LIMIT_SELL, ticker, 10, trader.get_best_price(ticker).get_ask_price())
                trader.submit_order(limit_buy)
                print("sell @", trader.get_last_price(ticker))
                signal = 'S'

            # Drop oldest price, shift the prices over, add the newest price to queue
            priceQueue[0]=priceQueue[1]
            priceQueue[1]=priceQueue[2]
            priceQueue[2]=trader.get_last_price(ticker)

        else: # Queue is not full
            priceQueue.append(trader.get_last_price(ticker)) # Fill the queue from oldest price to latest price
            """
        if count % 10 == 0:
            for order in trader.get_waiting_list():
                trader.submit_cancellation(order)

        time.sleep(lag)

        limit_buy = shift.Order(shift.Order.Type.LIMIT_BUY, ticker, 1, trader.get_best_price(ticker).get_bid_price())
        trader.submit_order(limit_buy)

        #time.sleep(lag)

        limit_sell = shift.Order(shift.Order.Type.LIMIT_SELL, ticker, 1, trader.get_best_price(ticker).get_ask_price())
        trader.submit_order(limit_sell)

        rightNow = dt.datetime.now() # Reset time rightNow

    # 90 seconds till end of trading day
    closePositions(trader, ticker, signal)

    # Done trading
    return


def main(argv):

    # Create trader object
    trader = shift.Trader(credentials.user) # **Change to competition user****************************************

    # Connect and subscribe to all available order books
    try:
        trader.connect("initiator.cfg", credentials.password) # **Change to competition password*****************************
        trader.sub_all_order_book() # Subscribe to orderbook for all tickers.  Can also choose one particular stock
    except shift.IncorrectPasswordError as e:
        print(e)
    except shift.ConnectionTimeoutError as e:
        print(e)

    # Today's date
    today = dt.date.today()

    # Datetime right now
    rightNow = dt.datetime.now()

    # Start of trading day datetime
    #startTime = dt.time(10,30,00) # **Competition time******************************
    startTime = dt.time(0,0,0) # **Set time for development**
    dayStart = dt.datetime.combine(today,startTime)

    # Wait to begin trading
    trafficLight(rightNow, dayStart, 0.5)

    # End of trading day datetime
    #endTime = dt.time(16,58,30) # **Competition time********************************
    endTime = dt.time(14,14,30) # **Set time for development**
    dayEnd = dt.datetime.combine(today,endTime)

    # Begin trading
    print("Initial buying power:",trader.get_portfolio_summary().get_total_bp())
    ticker = "BA"
    moneyMaker(trader, ticker, dayEnd, 2)
    
    # Disconnect
    print("Final buying power:",trader.get_portfolio_summary().get_total_bp())
    trader.disconnect()

    return


if __name__ == "__main__":
    main(sys.argv)


"""
time checks during simulation:
get_last_trade_time()

can assume moment code starts we can trade -- use get_last_trade_time() to
track time of day, so we can close the open positions


for item in trader.get_portfolio_items().values()
    if item.get_shares() > 0:
        trader.submit_order(shift.Order(shift.Order.Type.MARKET_SELL, item.get_symbol(), item.get_shares() / 100) # Order size in 100's of shares
    if item.get_shares() < 0:
        trader.submit_order(shift.Order(shift.Order.Type.MARKET_BUY, item.get_symbol(), item.get_shares() / (-100))

"""