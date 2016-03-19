import json
from matplotlib import pyplot as plt

from utility import *

logger.basicConfig(level=logger.INFO, format='> %(message)s')

input_files = ['gopatriots', 'gohawks', 'nfl', 'patriots', 'sb49', 'superbowl']  # tweet-data file names
feature_names = ['Number of Retweets', 'Number of Followers', 'Max Number of Followers',
                 'Impression Count', 'Favourite Count', 'Ranking Score', 'Hour of Day', 'Number of Users tweeting',
                 'Number of Long Tweets']  # features considered for regression model

logger.info("EXECUTING: QUESTION 3 - LINEAR REGRESSION WITH MORE FEATURES")

for file_name in input_files:
    logger.info("Calculating Statistics for #{}".format(file_name))
    tweets = open('../Dataset/tweet_data/tweets_#{0}.txt'.format(file_name), 'rb')
    first_tweet = json.loads(tweets.readline())
    start_time = first_tweet.get('firstpost_date')  # get the first tweet post time for window creation

    # features for model construction
    features = extra_feature_dict()
    current_window = 1
    end_time_of_window = start_time + current_window * 3600
    tweets.seek(0, 0)

    # store data
    tweet_features = []
    tweet_class = []
    logger.info("Extracting features from tweets")

    for tweet in tweets:
        tweet_data = json.loads(tweet)
        end_time = tweet_data.get('firstpost_date')

        if end_time < end_time_of_window:
            features = calculate_statistic(features, tweet_data)  # get stats of tweet data and update
        else:
            '''
            features : retweets, followers, max_followers, impressions, favorite_count,
                       ranking_score, hour_of_day, number_of_users, number_of_long tweets
            '''
            # append features to data variables
            extracted_features = get_features(features)
            tweet_class.append(extracted_features[0])
            tweet_features.append(extracted_features[1:])

            features = reset_features_dict()  # reset features for new window calculation
            features = calculate_statistic(features, tweet_data)  # update stats of tweet

            current_window += 1
            end_time_of_window = start_time + current_window * 3600  # update window

    tweet_class = np.roll(np.array(tweet_class), -1)
    # get transpose of the class variable
    tweet_class = collections.deque(tweet_class)
    tweet_class.rotate(-1)
    tweet_class = np.delete(tweet_class, -1)
    del (tweet_features[-1])


    result = sm.OLS(list(tweet_class), tweet_features).fit()
    sorted_p_values = sorted(range(len(result.pvalues)), key=lambda x: result.pvalues[x])
    sorted_t_values = sorted(range(len(result.tvalues)), key=lambda x: result.tvalues[x])[::-1]
    predicted = result.predict(tweet_features)
    logger.info('Fitting Accuracy: {}'.format(result.rsquared * 100))

    for i in range(1, 4):
        plt.figure(input_files.index(file_name) + i)
        plt.title("Scatter Plot {}".format(file_name))
        plt.xlabel("Number of Tweets / per hour")
        plt.ylabel(feature_names[sorted_p_values[i - 1]])
        plt.scatter(np.roll(np.array(tweet_class), 1), np.array(tweet_features)[:, sorted_p_values[i - 1]])
        plt.savefig("../Graphs/Question 3/Q3 - #{0} - Tweets vs {1}.png".format(file_name, feature_names[sorted_p_values[i-1]]))

    logger.info("**************************************************************************")
plt.show()
