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

# Number of spams
n_spam = training_data[57][training_data[57] == 1].count()

# Number of not spams
n_not_spam = training_data[57][training_data[57] == 0].count()

# Total rows of training data
total_ppl = training_data[57].count()

# Number of spams divided by the total rows
P_male = n_spam/total_ppl

# Number of not spams divided by the total rows
P_female = n_not_spam/total_ppl

# Group the data by spam or not spam and calculate the means of each feature
data_means = data.groupby(57).mean()

# Group the data by spam or not spam and calculate the variance of each feature
data_variance = data.groupby(57).var()

spam_mean = data_means[data_variance.index == 1].values[0]
spam_variance = data_variance[data_variance.index == 1].values[0]
not_spam_mean = data_means[data_variance.index == 0].values[0]
not_spam_variance = data_variance[data_variance.index == 0].values[0]


def p_x_given_y(data_points, mean_y, variance_y):
    """
    Calculates P(X|Y) for a column at a time
    """
    output = []
    for x in data_points:
        res = 1 / (np.sqrt(2 * np.pi * variance_y)) * np.exp((-(x - mean_y) ** 2) / (2 * variance_y))
        output.append(res)

    return output


# Standardizing testing feature data
testing_feature_data = (testing_data.iloc[:, :-1] - testing_data.iloc[:, :-1].mean()) /\
                       testing_data.iloc[:, :-1].std(ddof=1)

prob_spam = testing_feature_data.apply(lambda x: p_x_given_y(x.values, spam_mean[
           int(x.name)], spam_variance[int(x.name)]))

prob_not_spam = testing_feature_data.apply(lambda x: p_x_given_y(x.values, not_spam_mean[
           int(x.name)], not_spam_variance[int(x.name)]))

# Finding Maximum likelihood -- log exponential trick is also implemented below
mle_spam = np.exp(np.sum(np.log(prob_spam), axis=1))
mle_not_spam = np.exp(np.sum(np.log(prob_not_spam), axis=1))

# Finding estimated probability of test samples for both spam and not spam
p_est_spam__ytest = (P_male * mle_spam)
p_est_not_spam_ytest = (P_female * mle_not_spam)

# Lets get out predictions
testing_data['predictions'] = None
testing_data['tags'] = None
for i in range(len(p_est_spam__ytest)):
    if p_est_spam__ytest[i] > p_est_not_spam_ytest[i]:
        testing_data.iloc[i, 58] = 1
    else:
        testing_data.iloc[i, 58] = 0


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
