#******************************************************************
# Don't reinvent wheel. should just use pandas_market_calendars instead
# pip install pandas_market_calendars
#******************************************************************

from pandas.tseries.holiday import USFederalHolidayCalendar, HolidayCalendarFactory, GoodFriday

def getTradingCalendar():
    cal = USFederalHolidayCalendar()
    tradingCal = HolidayCalendarFactory('TradingCalendar', cal, GoodFriday)
    return tradingCal()


if __name__ == '__main__':
    tc = getTradingCalendar()
    tc.holidays