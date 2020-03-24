import numpy as np
import pandas as pd


data = pd.read_csv('x06Simple.csv').iloc[:, 1:]
data = data.sample(frac=1, random_state=0).reset_index(drop=True)  # Lets randomize our data with seed 0
target_data = data.iloc[:, 0]
feature_data = data.iloc[:, 1:]
feature_data = (feature_data - feature_data.mean())/feature_data.std()  # Standardizing
feature_data.insert(0, 'bias', 1)  # Adding the bias column to the training feature data

len_data = len(data)
data_divider = int(np.ceil((2/3)*len_data))  # 2/3 marker for splitting the data)

training_target_data = target_data.iloc[: data_divider]
testing_target_data = target_data.iloc[data_divider:]
testing_target_data = pd.DataFrame(testing_target_data.reset_index(drop=True))

training_feature_data = feature_data.iloc[: data_divider, :]
testing_feature_data = feature_data.iloc[data_divider:, :]

# The following formula is used below. theta = ((X.transpose*X)^-1)*X.transpose*Y
theta = np.dot(np.dot(np.linalg.inv(np.dot(training_feature_data.T, training_feature_data)), training_feature_data.T),
               training_target_data)

# Making the output string to display the final model
final_model = 'Final Model: Y = {}'
for i in range(len(theta)-1):
    final_model += ' + {}'
    final_model += '*X{}'.format(i+1)

print(final_model.format(*theta))

# Calculating RMSE
predicted_output = np.dot(testing_feature_data, pd.DataFrame(theta))
rmse = np.sqrt((testing_target_data.sub(predicted_output)).pow(2).sum()/len(predicted_output))

print('RMSE: {}'.format(rmse[0]))
