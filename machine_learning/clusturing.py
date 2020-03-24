import pandas as pd
import numpy as np
import copy
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import cv2


class Clustering:
    def __init__(self, k, features, data_path=r'diabetes.csv'):
        """

        :param k: The number of clusters
        :type k: int
        :param features: The features to be used in clustering
        :type features: list
        :param data_path: Path to CSV data file
        :type data_path: string
        """
        data = pd.read_csv(data_path, header=None)

        # Lets separate the class label from the observable data
        self.y = data[0]  # class labels
        x = data.iloc[:, features]  # observable data

        # We will need these for naming the output video files
        self.features = features
        self.data_path = data_path

        # Lets standardize our features
        self.x_std = (x - x.mean(0)) / (x.std(0))

        # Lets see if we need to do PCA
        if len(x.columns) > 3:
            self.x_std = self.do_three_pca()

        # Lets constraint the number of clusters to 7
        if k > 7:
            k = 7
            print("The number of clusters overwritten by program to 7")

        self.k = k

        # Lets decide on a color map for our clusters
        self.colormap = {1: 'r', 2: 'g', 3: 'b', 4: 'k', 5: 'm', 6: 'orange', 7: 'olive'}

        # Initializing the number of opencv video writers to zero
        self.num_of_vdo_writers = 0
        self.out_vid = None

        # Lets get out k_means
        self.my_k_means()

    def my_k_means(self):
        """
        This function runs k-means on the supplied data and value of k

        :return:
        """
        # Lets randomly select k centroids
        centroids = self.x_std.sample(self.k, random_state=0)  # random_state sets random seed to zero
        centroids.reset_index(inplace=True, drop=True)

        # Lets make a output data frame
        output_df = copy.deepcopy(self.x_std)

        # Lets assign our initial clusters
        output_df = self.assign_clusters(output_df, centroids)

        # We will keep on updating the centroids and their associated clusters until a termination cond is reached
        count = 0
        while True:
            count += 1
            old_centroids = copy.deepcopy(centroids)
            centroids = self.update_centroids(centroids, output_df)  # Lets update the centroids
            output_df = self.assign_clusters(output_df, centroids)  # lets assign the observations to the new centroids
            purity = self.get_purity(output_df)  # Let get the purity of our current clusters

            self.create_frames(output_df, centroids, count, purity)

            if abs(sum((old_centroids - centroids).sum())) < 2 ** -23:  # Termination condition
                self.out_vid.release()  # Lets release our video
                print('Clustering complete with {} iterations. The final purity achieved was {} %. Please check the '
                      'output video file for visualization.'.format(count, purity*100))
                break

    def get_purity(self, df):
        """
        Get purity of clusters from the passed data frame

        :param df: output_df from k-means iteration
        :return: Purity of the the clusters
        """
        df['class_labels'] = self.y  # Augmenting he class labels

        purity_temp = 0  # Setting initial purity to zero
        total_observations = 0  # Setting initial total observation to zero
        for i in range(self.k):
            df_i = df[df.closest == i+1]  # Extracts the observations that are closest to cluster i
            max_of_class_count = max(df_i.groupby('class_labels').count()['closest'])  # Gets max occurrence of labels
            num_in_cluster = len(df_i)  # Gets the number of observations in the cluster

            total_observations += num_in_cluster
            # purity_temp is used below in the full formula of purity
            purity_temp += num_in_cluster * ((1/num_in_cluster) * max_of_class_count)

        total_purity = (1/total_observations) * purity_temp

        return total_purity

    def create_frames(self, output_df, centroids, count, purity):
        """
        Creates multiples frame of a scatter plot  from different angles, to be used in the video
        """
        fig = plt.figure(figsize=(5, 5))
        num_cols = len(self.x_std.columns.values)

        if num_cols == 2 or num_cols == 1:
            ax = fig.add_subplot(111)
            ax.scatter(output_df.iloc[:, 0], output_df.iloc[:, 1], color=output_df['color'], alpha=0.5, marker='x')
            plt.title('Iteration: {}, Purity %: {}'.format(count, purity * 100))
        else:
            fig.add_subplot(111)
            ax = Axes3D(fig)
            ax.scatter(output_df.iloc[:, 0], output_df.iloc[:, 1], output_df.iloc[:, 2], color=output_df['color'],
                       alpha=0.5, marker='x')
            ax.text(0, 0, 5, 'Iteration: {}, Purity %: {}'.format(count, purity*100))

        for i in range(self.k):
            if num_cols == 2:
                ax.scatter(centroids.iloc[i, 0], centroids.iloc[i, 1], color=self.colormap[i + 1], edgecolor='k',
                           linewidths=2)
            elif num_cols == 1:
                ax.scatter(centroids.iloc[i, 0], 0, color=self.colormap[i + 1], edgecolor='k', linewidths=2)
            else:
                ax.scatter(centroids.iloc[i, 0], centroids.iloc[i, 1], centroids.iloc[i, 2], color=self.colormap[i + 1],
                           edgecolor='k', linewidths=2)

        try:
            ax.view_init(45, 90)  # Fixing frame viewing angle, if frame is 3d
        except AttributeError:
            pass

        plt.savefig('frame.png')
        img = cv2.imread('frame.png')
        plt.close()

        if self.num_of_vdo_writers == 0:
            shape = img.shape
            self.num_of_vdo_writers = 1
            # Lets define the codec and create VideoWriter object
            fourcc = cv2.VideoWriter_fourcc(*'XVID')

            if len(self.features) == 8 and self.data_path.endswith('diabetes.csv'):
                file_name = 'K_{}_F_{}.avi'.format(str(self.k), 'all')
            else:
                feature_string = ''
                for feature in self.features:
                    feature_string += '_{}'.format(feature)
                file_name = 'K_{}_F{}.avi'.format(str(self.k), feature_string)

            self.out_vid = cv2.VideoWriter(file_name, fourcc, 1.0, (shape[1], shape[0]))

        # Writing frame to video
        self.out_vid.write(img)

    def update_centroids(self, centroids, output_df):
        """
        Updates the location of the centroids

        :param centroids: current centroids
        :param output_df: current output_df from k-means
        :return: new centroids
        """
        for i in range(self.k):
            centroids.iloc[i, :] = np.mean(output_df[output_df['closest'] == i+1])

        return centroids

    def assign_clusters(self, output_df, centroids):
        """
        Assigns clusters to observations based on their closest centroid

        :param output_df: current output_df of k-means analysis
        :param centroids: current centroids of k-means analysis
        :return: updated output_df of k-means analysis
        """
        # Lets find the distance of the observations from each centroid
        for i in range(self.k):
            diff_sq = (self.x_std - centroids.iloc[i].values) ** 2
            output_df['distance_from_centroid_{}'.format(i+1)] = np.sqrt(diff_sq.sum(axis=1))

        # Lets get the name of the centroid distance columns
        centroid_distance_cols = ['distance_from_centroid_{}'.format(i+1) for i in range(self.k)]

        # Lets assign the closet centroid from each observation
        output_df['closest'] = output_df.loc[:, centroid_distance_cols].idxmin(axis=1)
        output_df['closest'] = output_df['closest'].map(lambda x: int(x.lstrip('distance_from_')))
        # Lets set a colormap for the clusters
        output_df['color'] = output_df['closest'].map(lambda x: self.colormap[x])
        return output_df

    def do_three_pca(self):
        """

        :return: A data frame of the three most important principle components
        """
        cov_matrix = np.cov(self.x_std.T)  # Finding the cov matrix

        w, v = np.linalg.eig(cov_matrix)  # Finding the eigenvalues and vectors

        # Lets sort the eigenvalues and vectors
        idx = w.argsort()[::-1]
        v = v[:, idx]

        return pd.DataFrame(np.matmul(self.x_std.values, v[:, [0, 1, 2]] * -1))


if __name__ == '__main__':
    # Lets read in the data
    num_k = input('Please enter a number for k:')

    # Indices for features start at 1.
    # For diabetes.csv if you wanted to run for all features please enter:1,2,3,4,5,6,7,8
    # For any csv file just enter the column indices of the features
    # For example, if you want the second and third features of a data set enter :2,3
    which_features = list(input('Please enter the features you want to include, in a comma separated fashion if you '
                                'enter more than one(eg. 1,2,3,4):'))[::2]
    which_features = [int(f) for f in which_features]

    clustering = Clustering(k=int(num_k), features=which_features)
