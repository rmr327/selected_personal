from PIL import Image
import numpy as np
import glob
import platform
import matplotlib.pyplot as plt
from matplotlib.pyplot import imshow


fig = plt.figure(figsize=(2, 3))

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

std = data_matrix.std(0)
mean = data_matrix.mean(0)
data_matrix = (data_matrix - mean) / std  # lets standardize the data matrix
cov_matrix = np.cov(data_matrix.T)  # Finding the cov matrix

w, v = np.linalg.eig(cov_matrix)  # Finding the eigenvalues and vectors

# Lets sort the eigenvalues and eigenvectors
idx = w.argsort()[::-1]
w = w[idx]
v = v[:, idx]

# Lets get our eigenvector corresponsing with the maximum eigenvalue
max_v = v[:, [0]] * -1
max_v_reshaped = np.resize(max_v, (40, 40)).astype(np.float64)  # Let's reshape the max eigenvector

# Lets normalize our pc to meet library requirements
max_v_min = np.min(np.min(max_v_reshaped))
max_v_max = np.max(np.max(max_v_reshaped))
max_v_scaled = np.interp(max_v_reshaped, (max_v_min, max_v_max), (0, 255))

im = Image.fromarray(max_v_scaled)  # Lets read the PC as an image
ax = fig.add_subplot(3, 2, 1)
ax.title.set_text('1) Primary Principle Component')
ax.set_xticks([])
ax.set_yticks([])
imshow(im)


# Single PC reconstruction
z = np.matmul(data_matrix[0, :], max_v)
x_ht = (np.matmul(z, max_v.T) * std) + mean
x_ht = np.resize(x_ht, (40, 40)).astype(np.float64)  # Let's reshape

# Lets normalize our matrix to meet library requirements
x_ht_min = np.min(np.min(x_ht))
x_ht_max = np.max(np.max(x_ht))
x_ht_scaled = np.interp(x_ht, (x_ht_min, x_ht_max), (0, 255))


im = Image.fromarray(x_ht_scaled)  # Lets get the image
ax1 = fig.add_subplot(3, 2, 3)
ax1.title.set_text('3) Single PC Reconstruction')
ax1.set_xticks([])
ax1.set_yticks([])
imshow(im)

# Lets get the original image
orig_im_data = (data_matrix[0, :] * std) + mean
orig_im_data = np.resize(orig_im_data, [40, 40])

# Lets extract the image
orig_im = Image.fromarray(orig_im_data)
ax2 = fig.add_subplot(3, 2, 2)
ax2.title.set_text('2) Original Image')
ax2.set_xticks([])
ax2.set_yticks([])
imshow(orig_im)

# Lets find k
k = 0
tot_w = np.sum(np.abs(w))  # sum of the absolute values of the eigenvalues
k_w = 0
percentage_of_w = 0
while percentage_of_w <= .95:
    k_w += abs(w[k])
    percentage_of_w = k_w / tot_w
    k += 1


# k PC reconstruction
k_v = v[:, list(range(k))] * -1
z = np.matmul(data_matrix[0, :], k_v)
x_ht = (np.matmul(z, k_v.T) * std) + mean
x_ht = np.resize(x_ht, (40, 40)).astype(np.float64)  # Let's reshape

# Lets normalize our matrix to meet library requirements
x_ht_min = np.min(np.min(x_ht))
x_ht_max = np.max(np.max(x_ht))
x_ht_scaled = np.interp(x_ht, (x_ht_min, x_ht_max), (0, 255))

im = Image.fromarray(x_ht_scaled)  # Lets get the image
ax3 = fig.add_subplot(3, 2, 4)
ax3.title.set_text('4) K (={}) PC Reconstruction'.format(k))
ax3.set_xticks([])
ax3.set_yticks([])
imshow(im)

# ALL pc reconstruction
z = np.matmul(data_matrix[0, :], v)
x_ht = (np.matmul(z, v.T) * std) + mean
x_ht = np.resize(x_ht, (40, 40)).astype(np.float64)  # Let's reshape

# Lets normalize our matrix to meet library requirements
x_ht_min = np.min(np.min(x_ht))
x_ht_max = np.max(np.max(x_ht))
x_ht_scaled = np.interp(x_ht, (x_ht_min, x_ht_max), (0, 255))

im = Image.fromarray(x_ht_scaled)  # Lets get the image
ax4 = fig.add_subplot(3, 2, 5)
ax4.title.set_text('5) Reconstruction using all eigenvectors')
ax4.set_xticks([])
ax4.set_yticks([])
imshow(im)

plt.show()
