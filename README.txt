Project: VCP Screener

Description:

I'm interested in stock investments and began learning about different indicators on YouTube, but it wasn't until I discovered Mark Minervini that I truly began to understand the strategy behind successful stock trading. Minervini is considered one of America's most successful stock traders and a two-time U.S. Investing Champion. To learn more about his strategy, I read his books: Trade Like a Stock Market Wizard and Think and Trade Like a Champion. Minervini uses many criteria to screen leading stocks, both fundamental and technical, but most trading platforms do not support setting so many indicator criteria. Therefore, I want to develop a screener.

Screener Details:

	1. The FinViz API by Mario Stoev will be used to screen stocks based on the following criteria:
	- Market cap is over $300 million to avoid trading micro or nano size stocks.
	- Average volume is over 100K.
	- Current price is over $2 to avoid trading micro or nano size stocks.
	- Current price is over 50MA (criteria 5 of trend template).
	- MA50 is above MA200 (criteria 4 of trend template).

	2. Minervini introduced a trend template, which identifies a stock in a Stage 2 uptrend if it meets the following eight criteria:
	- The current stock price is above both the 150-day and the 200-day moving average.
	- The 150-day moving average is above the 200-day moving average.
	- The 200-day moving average is trending up for at least one month.
	- The 50-day (10-week) moving average is above both the 150-day and 200-day moving averages.
	- The current price is above the 50-day moving average.
	- The current price is at least 30% above its 52-week low.
	- The current price is within at least 25% of its 52-week high.
	- The Relative Strength rating, as reported in Investor's Business Daily, is no less than 70.

	Since IBD prohibits data scraping, I cannot obtain stocks' RS rating. The RS rating tracks a stock's share price performance over the last 52 weeks, then compares the result to that of all other stocks. Therefore, I'll use the FinViz API again and sort the stocks by performance over a year.

	3. Volatility Contraction Pattern (VCP):
	- Price contraction: price consolidation occurs after a stock has moved up in price, allowing the stock to digest the bullish price movement. Price volatility will contract through the base from left to right, and price will correct through a series of smaller contractions. Ideally, this pattern should have 2 to 4 contractions.
	- Volume contraction: the volume usually decreases as the chart moves to the right.
	- Visualization:
		Visualize the chart of stocks with the current VCP.
	- Create a database:
		The list of stocks that meet the criteria will be stored in an Excel file, along with other parameters, such as the number of contractions, max contraction, min contraction, weeks of contraction, and RS rating. This can serve as a reference for a great VCP pattern.

Future Development:
	For Minervini's VCP pattern, there are still some other features that could be used to screen leading stocks:
	1. P/E
	2. EPS growth
	3. Industry group ranking
	4. Leadership in the group
	5. Etc.

Credits:

	1. Mario Stoev's Unofficial Python API for FinViz:
		FinViz provides market information and presents a wealth of data in visual snapshots, enabling traders and investors to quickly find the stocks, futures, or forex pairs they are seeking. The site offers advanced screeners, market maps, analysis, comparative tools, and charts. You can find the API at https://github.com/mariostoev/finviz.

	2. Minervini, Mark. (2013). Trade Like a Stock Market Wizard: How to Achieve Super Performance in Stocks in Any Market. McGraw-Hill.

	3. Minervini, Mark. (2017). Think and Trade Like a Champion: The Secrets, Rules and Blunt Truths of a Stock Market Wizard. McGraw-Hill.

Disclaimer:
	The information contained herein should not be construed as an offer, solicitation, or recommendation to buy or sell securities. We believe that the information has been obtained from reliable sources; however, we make no guarantee regarding its accuracy, timeliness, or completeness.