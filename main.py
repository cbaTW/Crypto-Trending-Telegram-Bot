import pandas as pd
import telegram
import traceback
import sys

def prepare():
    # 0. Count update interval
    # 1. Load old file as JSON
    df_old_bull = pd.read_json("bull.json")
    df_old_bear = pd.read_json("bear.json")
    return df_old_bull, df_old_bear


def perodic(bool):
    # TRUE for reset
    if bool:
        print('Perodic times reset from {} to 0 and sendUpdating Message'.format(perdoic_flag))
        with open('peridoic.txt', 'w') as f:
            f.write('0')
    # FALSE for keep
    else:
        print('Perodic times from {} plus 1 to {}.'.format(perdoic_flag, perdoic_flag+1))
        with open('peridoic.txt', 'w') as f:
            f.write(str(perdoic_flag+1))


def send_to_victim(p, flag):
    print('Send Message? {}'.format(flag))
    if flag and len(p)>0:
        perodic(True)
        p = p + '*- - - - - - - - - - - - - - - - - - - - -*\n'
        p = p.replace('!', '\!')
        p = p.replace('.', '\.')
        p = p.replace('-', '\-')
        # print(p)
        for i in AUDIENCES:
            bot.sendMessage(text=p, chat_id=i, parse_mode="MARKDOWNV2")


def extract(p):
    flag = True
    url = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=' + str(market_to_track) + '&page=1&sparkline=false&price_change_percentage=1h%2C24h&locale=en'

    df_old_bull = p[0]
    df_old_bear = p[1]

    df = pd.read_json(url)
    df = df[['symbol', 'price_change_percentage_1h_in_currency', 'price_change_percentage_24h_in_currency']]

    # 2. Fetch new data as JSON
    # 2-1. Filt and Sort new data
    sorting_key = 'price_change_percentage_' + str(hours_to_track) + 'h_in_currency'

    filt = (df[sorting_key] >= bull_require)
    df_bull = df.loc[filt, ['symbol', 'price_change_percentage_1h_in_currency', 'price_change_percentage_24h_in_currency']].sort_values(by='price_change_percentage_1h_in_currency', ascending=False)
    filt = (df[sorting_key] <= bear_require)
    df_bear = df.loc[filt, ['symbol', 'price_change_percentage_1h_in_currency', 'price_change_percentage_24h_in_currency']].sort_values(by='price_change_percentage_1h_in_currency', ascending=True)
    

    df_bull = df_bull.sort_values(by=sorting_key, ascending=False).round(2)
    df_bear = df_bear.sort_values(by=sorting_key, ascending=True).round(2)
    
    # 3 Process
    # 3-1. Bull
    # 3-1-1. Merge df
    try:
        df_merge_bull = pd.merge(left=df_old_bull, right= df_bull, left_on="symbol", right_on="symbol", how="right", suffixes=('_old', ''))
        # 3-1-2. Drop Old Price
        columns_to_drop = [col for col in df_merge_bull.columns if col.endswith('_old')]
        df_merge_bull.drop(columns=columns_to_drop, inplace=True)

        # 3-1-3. Find difference
        bull_newcomer = list(set(df_bull['symbol']) - set(df_old_bull['symbol']))
        bull_leaver = list(set(df_old_bull['symbol']) - set(df_bull['symbol']))
    except KeyError:
        df_merge_bull = df_bull
        bull_newcomer = list(set(df_bull['symbol']))
        bull_leaver = list()
    except Exception as e:
        traceback.print_exc()
        flag = False
        pass

    # 3-2. Bear
    # 3-2-1. Merge df
    try:
        df_merge_bear = pd.merge(left=df_old_bear, right= df_bear, left_on="symbol", right_on="symbol", how="right", suffixes=('_old', ''))
        # 3-2-2. Drop Old Price
        columns_to_drop = [col for col in df_merge_bear.columns if col.endswith('_old')]
        df_merge_bear.drop(columns=columns_to_drop, inplace=True)

        # 3-2-3. Find difference
        bear_newcomer = list(set(df_bear['symbol']) - set(df_old_bear['symbol']))
        bear_leaver = list(set(df_old_bear['symbol']) - set(df_bear['symbol']))
    except KeyError:
        df_merge_bear = df_bear
        bear_newcomer = list(set(df_bear['symbol']))
        bear_leaver = list()

    except Exception as e:
        traceback.print_exc()
        flag = False
        pass

    # 4. Save New df to File.json
    df_merge_bull.to_json('bull.json', orient='records')
    df_merge_bear.to_json('bear.json', orient='records')

    # 5.Message Concat

    # 5-1. Message Variable
    str_op_new = '*- - - - - New Trending!- - - - -*\n\n'
    str_news_bull_in_front = 'New Bull:\n*'
    str_news_bull_out_front = 'Bye Bull:\n*'
    str_news_bear_in_front = 'New Bear:\n*'
    str_news_bear_out_front = 'Bye Bear:\n*'
    str_news_back = '*\n\n'
    leaderboard = ''

    # 5-2. concating and sending message
    if flag:
        # Leader board Concating
        print(len(df_merge_bull.index))
        print(len(df_merge_bear.index))
        if len(df_merge_bull.index) or len(df_merge_bear.index):
            leaderboard = '*- - - - - -LeaderBoard- - - - - -*\n'
            if len(df_merge_bull.index):
                leaderboard += 'Bull:\n```\n'
                for index, row in df_merge_bull.iterrows():
                    leaderboard += '${:<7} {: >6.2f}%  {: >6.2f}%\n'.format(row[0].upper(), row[1], row[2])
                leaderboard += '```\n\n\n\n'
            if len(df_merge_bear.index):
                leaderboard += 'Bear:\n```\n'
                for index, row in df_merge_bear.iterrows():
                    leaderboard += '${:<7} {: >6.2f}%  {: >6.2f}%\n'.format(row[0].upper(), row[1], row[2])
                leaderboard += '```\n'

        # Trending Concating
        news = ''
        if (len(bull_newcomer)>0 or len(bull_leaver)>0 or len(bear_newcomer)>0 or len(bear_leaver)>0):
            news = str_op_new
            if len(bull_newcomer) > 0:
                news += str_news_bull_in_front
                for i in bull_newcomer:
                    news += '{}   '.format(i.upper())
                news += str_news_back
            if len(bull_leaver) > 0:
                news += str_news_bull_out_front
                for i in bull_leaver:
                    news += '{}   '.format(i.upper())
                news += str_news_back
            if len(bear_newcomer) > 0:
                news += str_news_bear_in_front
                for i in bear_newcomer:
                    news += '{}   '.format(i.upper())
                news += str_news_back
            if len(bear_leaver) > 0:
                news += str_news_bear_out_front
                for i in bear_leaver:
                    news += '{}   '.format(i.upper())
                news += str_news_back
        if len(news) > 0:
            send_to_victim(news+leaderboard, flag)
        elif perdoic_flag >= update_interval:
            send_to_victim(leaderboard, flag)
        else:
            perodic(False)
            
        # Send Function
    else:
        send_to_victim('', flag)



        

def main():
    # print(AUDIENCES)
    try:
        extract(prepare())
    except Exception as e:
        traceback.print_exc()


if __name__ == '__main__':
    try:
        TELEGRAM_TOKEN = sys.argv[1]
        bot = telegram.Bot(TELEGRAM_TOKEN)
        AUDIENCES = sys.argv[2]
        AUDIENCES = AUDIENCES.split(',')
        with open('peridoic.txt', 'r') as f:
            perdoic_flag = int(f.read())

        update_interval = 5
        bull_require = 2.5
        bear_require = -3 # negative need
        hours_to_track = 24 # 1 or 24
        market_to_track = 125 # 1~250
        
        main()
    except Exception as e:
        traceback.print_exc()
