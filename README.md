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
The National Centers for Environmental Information (NCEI) (previously known as the National Climatic Data Center (NCDC) which dissolved in 2015) are operated in part by an office of the National Oceanographic and Atmospheric Administration (NOAA). The NCDC data set 3260 (DSI-3260) also known as the 15 Minute Precipitation Data is available from 1971 through 2013. Since geo-location station data is not found for this period, I use the geo-location station data in NCEI’s 2014 and onwards Hourly Precipitation Data set (HPDv2 beta version). I focus on 2018-2019 data from the DSI-32604 and the HPDv2 beta version5 that provides 15-minute precipitation intervals. The raw data have some unreasonable values (e.g., negative precipitation), and I correct these observations with 0. I intersect the HDPv2 station data with the the 2011-2013 DSI-3260 station data to obtain a list of weather stations operating in Illinois, Indiana, Michigan, Ohio, Pennsylvania, and New Jersey for 2018-2019.
