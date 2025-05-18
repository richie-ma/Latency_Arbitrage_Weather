# Revisit: Latency Arbitrage under Different Weather Conditions

## Author
<img src="images/ma_richie220922-mh-01.jpg" alt="Richie Ma" width="150"/>

Richie Ma is a Ph.D. student who is drawn to research on financial market microstructure and high-frequency trading. He has a good sense of market microstructure in the U.S. stock, ETF, and futures markets. His recent research mainly focuses on microstructure in the CME futures markets, specifically market liquidity. He has experience on parsing CME market data, inclduing both FIX and binary protocols, reconstructing limit order book, and analyzing big data in both Python and R languages. His recent publication analyzes order-level details in three CME commodity markets and reveals that quote updates instead of trades have been the main driver of market price. He is a member of Bielfeldt Office for Futures and Options Research and currently a teaching assistant at Department of Industrial & Enterprise Systems Engineering at the University of Illinois. 

His technical skill set includes proficiency in financial market microstructure, R, and Python. He co-authored an R package `cme.mdp` with Brian Peterson and he is also creating similar pacakges in Python.

## Introduction

Latency arbitrage is one of the most popular ultra-low latency stratgies in the high-frequency trading industry and literature has suggested that this strategy can indeed make great profits. During the last decade, some high-frequency trading firms may use the microwave to implement latency arbitrage instead of fiber optic cables to become slightly faster than other market participants. However, since the microwave is more prone to weather disruption, especially during the heavy raining period. This project uses some recent data, from August 2018 to December 2019 to assess latency arbitrage between CME E-mini S&P 500 futures and SPDR S&P 500 ETF (SPY).

## Data
In this section, I discuss both the precipitation data and the market data.
### Weather data
The National Centers for Environmental Information (NCEI) (previously known as the National Climatic Data Center (NCDC) which dissolved in 2015) are operated in part by an office of the National Oceanographic and Atmospheric Administration (NOAA). The NCDC data set 3260 (DSI-3260) also known as the 15 Minute Precipitation Data is available from 1971 through 2013. Since geo-location station data is not found for this period, I use the geo-location station data in NCEI’s 2014 and onwards Hourly Precipitation Data set (HPDv2 beta version). I focus on 2018-2019 data from the DSI-32604 and the HPDv2 beta version5 that provides 15-minute precipitation intervals. The raw data have some unreasonable values (e.g., negative precipitation), and I correct these observations with 0. I intersect the HDPv2 station data with the the 2011-2013 DSI-3260 station data to obtain a list of weather stations operating in Illinois, Indiana, Michigan, Ohio, Pennsylvania, and New Jersey for 2018-2019. The HPDv2 beta version readme file states precipitation data is in hundredths of an inch. My station list is as follows:
| Station ID    | Latitude | Longitude | State | Name                        |
|---------------|----------|-----------|-------|-----------------------------|
| USC00111577   | 41.7372  | -87.7775  | IL    | CHICAGO MIDWAY AP 3SW      |
| USC00112011   | 41.4492  | -87.6221  | IL    | CRETE                       |
| USC00114603   | 41.1351  | -87.8856  | IL    | KANKAKEE METRO WASTEWATER  |
| USC00115825   | 41.3708  | -88.4336  | IL    | MORRIS 1 NW                |
| USC00120200   | 41.6639  | -85.0183  | IN    | ANGOLA                     |
| USC00120830   | 40.8143  | -85.1546  | IN    | BLUFFTON 6N                |
| USC00121147   | 40.4835  | -86.3961  | IN    | BURLINGTON                 |
| USC00121417   | 40.6653  | -86.9550  | IN    | CHALMERS 5 W               |
| USC00121739   | 41.1452  | -85.4898  | IN    | COLUMBIA CITY              |
| USC00123206   | 41.3415  | -85.1292  | IN    | GARRETT                    |
| USC00123418   | 41.5575  | -85.8825  | IN    | GOSHEN 3SW                 |
| USC00124181   | 40.8555  | -85.4980  | IN    | HUNTINGTON                 |
| USC00124782   | 41.5269  | -86.2692  | IN    | LAKEVILLE                  |
| USC00124837   | 41.6116  | -86.7297  | IN    | LAPORTE                    |
| USC00125337   | 40.5800  | -85.6586  | IN    | MARION 2 N                 |
| USC00126864   | 40.7646  | -86.0740  | IN    | PERU                       |
| USC00127069   | 40.4667  | -84.9667  | IN    | PORTLAND WATER WORKS      |
| USC00127298   | 40.9239  | -87.1754  | IN    | RENSSELAER                 |
| USC00127482   | 41.0665  | -86.2096  | IN    | ROCHESTER                  |
| USC00129724   | 41.1645  | -84.8482  | IN    | WOODBURN 3N                |
| USC00330059   | 41.1573  | -81.5664  | OH    | AKRON WPCS                 |
| USC00330107   | 40.9551  | -81.1167  | OH    | ALLIANCE 3 NNW             |
| USC00330493   | 40.6335  | -81.5577  | OH    | BEACH CITY LAKE           |
| USC00330639   | 41.1169  | -81.0094  | OH    | BERLIN LAKE               |
| USC00330862   | 41.3831  | -83.6111  | OH    | BOWLING GREEN WWTP        |
| USC00331042   | 41.4619  | -84.5272  | OH    | BRYAN 2 SE                |
| USC00331466   | 40.7333  | -82.3667  | OH    | CHARLES MILL LAKE         |
| USC00332098   | 41.2783  | -84.3847  | OH    | DEFIANCE                  |
| USC00332272   | 40.5622  | -81.4092  | OH    | DOVER DAM                 |
| USC00332791   | 41.0461  | -83.6622  | OH    | FINDLAY WPCC              |
| USC00333021   | 40.7231  | -82.7999  | OH    | GALION WATER WORKS        |
| USC00334473   | 40.4709  | -81.1955  | OH    | LEESVILLE LAKE            |
| USC00334551   | 40.7247  | -84.1294  | OH    | LIMA WWTP                 |
| USC00334942   | 40.6142  | -83.1300  | OH    | MARION 2 N                |
| USC00334992   | 40.7667  | -81.5333  | OH    | MASSILLON                 |
| USC00335297   | 40.5375  | -81.9197  | OH    | MILLERSBURG               |
| USC00336123   | 41.2500  | -82.6167  | OH    | NORWALK HIWAY DEPT        |
| USC00336196   | 41.2802  | -82.2187  | OH    | OBERLIN                   |
| USC00336702   | 40.6245  | -82.3271  | OH    | PLEASANT HILL LAKE        |
| USC00336949   | 41.1366  | -81.2844  | OH    | RAVENNA 2 S               |
| USC00337383   | 40.5449  | -84.4374  | OH    | ST. MARYS 3 W             |
| USC00338313   | 41.1167  | -83.1667  | OH    | TIFFIN                    |
| USC00338539   | 40.8428  | -83.2767  | OH    | UPPER SANDUSKY WTR WK     |
| USC00339312   | 40.7833  | -81.9167  | OH    | WOOSTER EXP STATION       |
| USC00360147   | 41.3579  | -77.9264  | PA    | ALVIN R BUSH DAM          |
| USC00360560   | 40.8620  | -75.6429  | PA    | BELTZVILLE DAM            |
| USC00360725   | 40.3027  | -77.5894  | PA    | BLAIN 5SW                 |
| USC00360785   | 40.3803  | -76.0275  | PA    | BLUE MARSH LAKE           |
| USC00360821   | 40.1597  | -79.0287  | PA    | BOSWELL                   |
| USC00361139   | 40.8415  | -79.9163  | PA    | BUTLER 2 SW               |
| USC00361961   | 40.9583  | -78.5294  | PA    | CURWENSVILLE LAKE         |
| USC00362245   | 41.3421  | -78.1401  | PA    | DRIFTWOOD                 |
| USC00362323   | 41.5216  | -76.4043  | PA    | DUSHORE                   |
| USC00363018   | 41.1184  | -75.7277  | PA    | FRANCIS E WALTER DAM      |
| USC00363028   | 41.4004  | -79.8305  | PA    | FRANKLIN                  |
| USC00364001   | 40.4388  | -78.4173  | PA    | HOLLIDAYSBURG 2NW         |
| USC00364325   | 41.4992  | -80.4681  | PA    | JAMESTOWN 2 NW            |
| USC00364432   | 41.6770  | -78.8036  | PA    | KANE 1NNE                 |
| USC00364778   | 40.1190  | -76.4265  | PA    | LANDISVILLE 2 NW          |
| USC00365790   | 40.8847  | -77.4750  | PA    | MILLHEIM                  |
| USC00366111   | 40.4120  | -79.7245  | PA    | MURRYSVILLE 2 SW          |
| USC00366233   | 41.0172  | -80.3615  | PA    | NEW CASTLE 1 N            |
| USC00366916   | 40.9017  | -78.0842  | PA    | PHILIPSBURG 8 E           |
| USC00367186   | 41.5890  | -75.3303  | PA    | PROMPTON DAM              |
| USC00367229   | 40.9248  | -79.2825  | PA    | PUTNEYVILLE 2 SE DAM      |
| USC00367931   | 40.8153  | -76.8556  | PA    | SELINSGROVE CAA AIRPORT   |
| USC00367938   | 40.3552  | -75.3131  | PA    | SELLERSVILLE              |
| USC00368057   | 41.1831  | -76.1488  | PA    | SHICKSHINNY 3 N           |
| USC00368491   | 41.6972  | -75.4827  | PA    | STILLWATER DAM            |
| USC00368873   | 41.4792  | -79.4432  | PA    | TIONESTA 2 SE LAKE        |

Here, I show a summary statistics of the precipitation during the whole sample period. Obviously, one can find that for each weather station across the whole sample period, the average precipitation is just 0.08 inches and the largest precipitation is 3.1 inches.
|       |   precipitation |
|-------|-----------------|
| count |    9990         |
| mean  |       0.0791802 |
| std   |       0.178167  |
| min   |       0         |
| 25%   |       0         |
| 50%   |       0.01      |
| 75%   |       0.06      |
| max   |       3.1       |

## Market Data
In terms of futures data, I use the CME Market by Price (MBP) data provided by CME Datamine and I select the most-traded futures contracts according to the daily trading volume. For SPY data, I use the Daily Trade and Quote (TAQ) data. Specifically, I focus on the Millisecond Trades and NBBO data. Since the CME futures is traded during 18:00 to 17:00 ET while the ETF is traded during 9:30 to 16:00 ET, I concentrate regular trading hours from 9:30 to 16:00 ET. I find almost all trades are assigned the direction (e.g., buyer-initiated/seller-initiated) directly by the CME while no trade direction is assigned in the ETF by the data. Hence, I follow Lee and Ready (1991) to assign its trade direction, including both quote test and tick test. 

# Market liquidity and precipitation
Market liquidity is likely to be affected by the precipitation with the importance of communciation increasing. Market makers may reduce their liquidity provision during heavy precipitation period, because of both communication delay and picking off risks. Thus, I first assess how the precipitation affects the market liquidity during the heavy precipitation



