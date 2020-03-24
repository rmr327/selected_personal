import numpy as np
import pandas as pd


def chunk_it(indices, num_of_parts):
    """Divided the pasees indices in num_of_parts"""
    avg = len(indices) / float(num_of_parts)
    out = []
    last = 0.0

    while last < len(indices):
        out.append(indices[int(last):int(last + avg)])
        last += avg

    return out


def s_folds(s_val, data):
    """
    Calulates the S-fold cross validation mean of RMSE and STD of RMSE over 20 runs
    :param s_val: Number of fols
    :type s_val: inr
    :param data: csv data
    :type data: pandas data frame
    :return: Mean(RMSE of the 20), STD(RMSE of the 20)
    """
    n = len(data)  # Number of observations
    s = [3, 5, 20, n]  # The fold values
    rmse = []

    for j in range(20):  # lets do this 20 times.
        ss = s[s_val]
        data = data.sample(frac=1, random_state=0).reset_index(drop=True)  # Lets randomize our data with seed 0
        target_data = data.iloc[:, 0]
        feature_data = data.iloc[:, 1:]
        feature_data = (feature_data - feature_data.mean()) / feature_data.std()  # Standardizingl
        feature_data.insert(0, 'bias', 1)  # Adding the bias column to the training feature data

        sqe_rmse = []  # Lets initialize a list to hold the rmse values of each fold
        indices = chunk_it(list(range(n)), ss)

        for i in range(ss):
            testing_indices = [indices[p][j] for p in range(len(indices)) for j in range(len(indices[p])) if p != i]

            testing_target_data = target_data.iloc[indices[i]]
            training_target_data = target_data.iloc[testing_indices]
            testing_target_data = pd.DataFrame(testing_target_data.reset_index(drop=True))
            testing_feature_data = feature_data.iloc[indices[i], :]
            training_feature_data = feature_data.iloc[testing_indices, :]

            # The following formula is used below. theta = ((X.transpose*X)^-1)*X.transpose*Y
            theta = np.dot(
                np.dot(np.linalg.inv(np.dot(training_feature_data.T, training_feature_data)), training_feature_data.T),
                training_target_data)

            # Calculating rmse for this fold and adding to sqe_rmse
            predicted_output = np.dot(testing_feature_data, pd.DataFrame(theta))
            sqe_rmse.append(np.sqrt(np.sum((testing_target_data-predicted_output)**2)/len(predicted_output)))

        rmse.append((sum(sqe_rmse)/len(sqe_rmse)))

    return np.mean(rmse), np.std(rmse)


if __name__ == '__main__':
    csv_data = pd.read_csv('x06Simple.csv').iloc[:, 1:]
    s_fold_vals = [3, 5, 20, len(csv_data)]

    print_str = 'Number of fold: {} ; Average of RMSE: {}; STD of RMSE: {}'
    for fold in range(len(s_fold_vals)):
        mean_val, std_val = s_folds(fold, csv_data)
        print(print_str.format(s_fold_vals[fold], mean_val, std_val))
