# Pump and dump dataset
This repository contains an extended version of the dataset used for the paper:

[Pump and Dumps in the Bitcoin Era: Real Time Detection of Cryptocurrency Market Manipulations](https://ieeexplore.ieee.org/document/9209660)

If you use this dataset, or use the findings from the paper, please cite:

```
@INPROCEEDINGS{9209660,
  author={M. {La Morgia} and A. {Mei} and F. {Sassi} and J. {Stefa}},
  booktitle={2020 29th International Conference on Computer Communications and Networks (ICCCN)}, 
  title={Pump and Dumps in the Bitcoin Era: Real Time Detection of Cryptocurrency Market Manipulations}, 
  year={2020},
  pages={1-9},
  doi={10.1109/ICCCN49398.2020.9209660}
  }
```


## The dataset

The dataset contains a list of pump and dumps arranged by groups on Telegram. See the paper for a more detailed description of the dataset generation process.
The pump events are listed inside the ```pump_telegram.csv``` file.


### The pump and dumps file (```pump_telegram.csv```)

Each row of this file contains:
* **symbol**: the symbol (SYM) of the pumped coin. 
* **group**: the code of the group that arranged the pump and dump. More information about the groups can the found in the ```group.csv``` file
* **date**: the pump and dump date
* **hour**: the pump and dump hour expressed in UTC
* **exchange**: the exchange targeted by the group

***All the pump and dumps in the dataset are on the trading pair SYM/BTC.***


We provide a script to download the transactions from the Binance exchange that we used to train the machine learning model.
Each transaction contains the following fields, check the [Binance documentation](https://binance-docs.github.io/apidocs/spot/en/#old-trade-lookup) for further information:
* **timestamp**: the timestamp of the transaction
* **datetime**: the datetime of the transaction
* **side**: indicates the type of the transaction: sell or buy
* **price**: the trading price 
* **amount**: the amount of money traded
* **btc_volume**: the trading volume expressed in BTC

### The group file (```group.csv```)

* **group_name**: The name of the pump and dump group
* **group_code**: Abbreviation used in the dataset for the group
* **last_time_checked**: Last time we retrieved the pump and dumps arranged by the group from the Telegram channel
* **telegram_link**: Link to the Telegram channel of the group

# Contribution

***Your contribution is very welcome!***

If you want to help us maintain the dataset updated, feel free to create a pull request.

Please, make sure to fill all the fields of the ```pump_telegram.csv``` in your pull request.
If you add pump and dumps arranged by groups that are not in the ```group.csv``` file, please update this file as well.

We will review your pull request and merge it on the master branch or contact you for additional information.


# Installation
Clone this repository and run:

```
pip3 install -r requirements.txt
```
To download all the transactions of the pump and dumps carried out on Binance run the ```downloader.py``` script.

```
python3 downloader.py
```

To compute the features for the machine learning model, run the ```features.py``` script.
```
python3 features.py
```
It generates 3 features files, one for each chunk size (5, 15, 25 secs). The features are stored in csv files contained in the
```features``` folder.

The computed features are the following:

* **StdRushOrders** and **AvgRushOrders**: : Moving standard deviation and average of the number of rush orders in each chunk of the moving window.

* **StdTrades**: Moving standard deviation of the number of trades.

* **StdVolumes** and **AvgVolumes**: Moving standard deviation and average of volume of trades in each chunk of the moving window.

* **StdPrice** and **AvgPrice**: Moving standard deviation and average of closing price. 

* **AvgPriceMax** : Moving average of maximal and minimum price in each chunk.



During our analysis, we found that in some cases, pump and dumps started before or after the organizer shared the signal. To account for this discrepancy, we look into the trading data and manually flag the chunk when the pump and dump actually started.
For this reason, the labeled chunk may be up to 120 seconds before the time reported in the  ```pump_telegram.csv``` file. 
This case is usually due to a pre-pump on the targeted coin by the admin.
We provide the labeled features in the ```labeled features``` folder.

In order to execute our classifier on our labeled features run the ```classifier.py``` file
```
python3 classifier.py
```

# Donation
If you enjoyed our work, you can buy us a cup of coffee :coffee: donating on this Zcash wallet:

```
zs1uw83xkwr2rl3hrphxy0sdpnvlgusy9au940af5423f06ntxev6qqzu7hqwhmn5td5a035jzczt9
```

[![zs1uw83xkwr2rl3hrphxy0sdpnvlgusy9au940af5423f06ntxev6qqzu7hqwhmn5td5a035jzczt9](./wallet/wallet.png?raw=true "Title")](#)
