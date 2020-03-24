import pandas as pd
import numpy as np


data = pd.read_csv('spambase.data', header=None)  # Reading in data
data = data.sample(frac=1, random_state=0).reset_index(drop=True)  # Lets randomize our data with seed 0

# Splitting testing and training data
len_data = len(data)
data_divider = int(np.ceil((2 / 3) * len_data))  # 2/3 marker for splitting the data)
training_data = data.iloc[: data_divider]
testing_data = data.iloc[data_divider:]
testing_data = pd.DataFrame(testing_data.reset_index(drop=True))

# Standardizing training data
training_data.iloc[:, :-1] = (training_data.iloc[:, :-1] - training_data.iloc[:, :-1].mean()) / \
                             training_data.iloc[:, :-1].std(ddof=1)


def sigmoid(scores):
    return 1 / (1 + np.exp(-scores))


def log_likelihood(features, target, weights):
    scores = np.dot(features, weights)
    ll = np.sum(target*scores - np.log(1 + np.exp(scores)))
    return ll


def logistic_regression(features, target, learning_rate):
    # Lets add a bias col
    bias_col = np.ones((features.shape[0], 1))
    features = np.hstack((bias_col, features))

    weights = np.zeros(features.shape[1])

    while True:
        scores = np.dot(features, weights)
        predictions = sigmoid(scores)

        old_log_likelihood = log_likelihood(features, target, weights)

        # Update weights with gradient
        output_error_signal = target - predictions
        gradient = np.dot(features.T, output_error_signal)
        weights += learning_rate * gradient

        new_log_likelihood = log_likelihood(features, target, weights)

        if abs(abs(new_log_likelihood) - abs(old_log_likelihood)) < 0.1:
            break

    return weights


weight_s = logistic_regression(training_data.iloc[:, :-1], training_data.iloc[:, -1], learning_rate=5e-5)

# Standardizing testing feature data
testing_feature_data = (testing_data.iloc[:, :-1] - testing_data.iloc[:, :-1].mean()) /\
                        testing_data.iloc[:, :-1].std(ddof=1)

# Testing features with added bias column
testing_feature_data = np.hstack((np.ones((testing_feature_data.shape[0], 1)), testing_feature_data))
# Lets get our predictions
test_spam_probability_predictions = sigmoid(np.dot(testing_feature_data, weight_s))

# Lets assign the appropriate class to our predictions
testing_data['predictions'] = None
for i in range(len(test_spam_probability_predictions)):
    if 1 - test_spam_probability_predictions[i] > 0.5:
        testing_data.iloc[i, -1] = 0
    else:
        testing_data.iloc[i, -1] = 1


def assign_tags(row):
    """
    assign tags to later compute performance metrics
    """
    if row[57] == 1 and row.predictions == 1:
        return 'tp'
    elif row[57] == 0 and row.predictions == 0:
        return 'tn'
    elif row[57] == 0 and row.predictions == 1:
        return 'fp'
    else:
        return 'fn'


testing_data['tags'] = testing_data.apply(lambda row: assign_tags(row), axis=1)  # Assigning performance tags

# Tallying performance tags
tp = testing_data['tags'][testing_data['tags'] == 'tp'].count()
tn = testing_data['tags'][testing_data['tags'] == 'tn'].count()
fp = testing_data['tags'][testing_data['tags'] == 'fp'].count()
fn = testing_data['tags'][testing_data['tags'] == 'fn'].count()

prec = tp/(tp+fp)  # precision
rec = tp/(tp+fn)  # recall
f_m = (2*prec*rec)/(prec+rec)  # F-measure
acc = (tp+tn)/(tp+tn+fp+fn)  # accuracy

# Lets print out our results
print('Precision: {}%'.format(prec*100))
print('Recall: {}%'.format(rec*100))
print('F-measure: {}%'.format(f_m*100))
print('Accuracy: {}%'.format(acc*100))
