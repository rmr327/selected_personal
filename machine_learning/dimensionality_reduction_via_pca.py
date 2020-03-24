from PIL import Image
import numpy as np
import glob
import platform
import matplotlib.pyplot as plt


# Lets see what OS the user is running this from
current_os = platform.platform()
# Lets fix our file location accordingly
if current_os.startswith('Win'):
    file_directory = r'yalefaces\subject*'
else:
    file_directory = r'yalefaces/subject*'  # For Linux systems

data_matrix = np.zeros((154, 1600))  # Initializing our data matrix
all_files = glob.glob(file_directory)
for i in range(len(all_files)):  # iterates over all files in specified directory
    # The purpose of the try and except block is to ignore the readme file
    im = Image.open(all_files[i])  # Read in the image as a 2D array (234x320 pixels)
    im = im.resize((40, 40))  # resize the image to become a 40x40 pixel image
    im = im.getdata()  # Flatten the image to a 1D array (1x1600)
    data_matrix[i, :] = np.asarray(im)  # Adding the flattened data as a row

data_matrix = (data_matrix - data_matrix.mean(0)) / (data_matrix.std(0))  # lets standardize the data matrix
cov_matrix = np.cov(data_matrix.T)  # Finding the cov matrix

w, v = np.linalg.eig(cov_matrix)  # Finding the eigenvalues and vectors

max_w = np.amax(w)  # Finding max eigenvalue
max_index = np.where(w == max_w)  # Finding corresponding index
max_v = v[:, max_index[0]]  # Finding corresponding eig vector

# Lets update our eig values and vectors by removing the last picked values
w = np.delete(w, max_index)
v = np.delete(v, max_index, axis=1)

# Lets find our second largest eigenvalue and vector pair
max_w_1 = np.amax(w)  # Finding max eigenvalue
max_index_1 = np.where(w == max_w_1)  # Finding corresponding index
max_v_1 = v[:, max_index_1[0]]  # Finding corresponding eig vector

v_tot = np.concatenate((max_v, max_v_1), axis=1) * -1  # This is our final eigenvectors
pca_proj = np.matmul(data_matrix, v_tot)  # Lets project the points

plt.scatter(pca_proj[:, 0], pca_proj[:, 1], facecolors='none', edgecolors='r')
plt.title('PCA Projection of Data')
plt.show()
