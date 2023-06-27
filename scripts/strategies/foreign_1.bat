Rem Overall config
set strategy=Foreign1
set time_start=20220701
set time_finish=20220801
set timeframes=5m 1d
set config_test=config_backtest.json
set config_prod=config_backtest.json

Rem Hyperopt Config 
set hyperopt_reps=10
set hyperopt_spaces=buy sell
set hyperopt_loss=SharpeHyperOptLoss

if %1%==backtest (
docker compose run --rm freqtrade download-data --timerange %time_start%-%time_finish% --timeframes %timeframes% --config user_data/%config_test% --prepend
docker compose run --rm freqtrade backtesting --timerange %time_start%-%time_finish% --strategy %strategy% --config user_data/%config_test%
)

if %1%==hyperopt (
docker compose run --rm freqtrade download-data --timerange %time_start%-%time_finish% --timeframes %timeframes% --config user_data/%config_test% --prepend
docker compose run --rm freqtrade hyperopt --config user_data/%config_test% --timerange %time_start%-%time_finish% --hyperopt-loss %hyperopt_loss% --strategy %strategy% -e %hyperopt_reps% --spaces %hyperopt_spaces% --config user_data/%config_test%
)

if %1%==plot_dataframe (
docker compose -f docker-compose-plot.yml run --rm freqtrade plot-dataframe --strategy %strategy% --timeframe %timeframes% --timerange %time_start%-%time_finish% --config user_data/%config_test%
)

if %1%==plot_profit (
docker compose -f docker-compose-plot.yml run --rm freqtrade plot-profit --strategy %strategy% --timeframe %timeframes% --timerange %time_start%-%time_finish% --config user_data/%config_test%
)

if %1%==trade_test (
docker compose run --rm freqtrade trade --config user_data/%config_test% --strategy %strategy%
)

if %1%==trade_prod (
docker compose run --rm freqtrade trade --config user_data/%config_prod% --strategy %strategy%
)


