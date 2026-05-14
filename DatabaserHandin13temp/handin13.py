import numpy as np
from numpy.ma.extras import unique


class KMeansClassifier:

    """ This classifier was implemented by myself, when following the course Machine Learning and Statistical Learning.
    It is based on the litterature from Bishop: Pattern Recognition and Machine Learning
    """
    def __init__(self, data, initial_means, test_labels, k, max_iters=100):
        self.data = data
        self.labels = None  # Initialize labels to None
        self.test_labels = test_labels
        self.k = k
        self.clusters = np.unique(test_labels)  # Cluster labels from 1 to k
        self.n, self.d = data.shape
        self.max_iters = max_iters

        self.mean_k = initial_means  # Shape (k, d)

    def compute_mean_k(self, print_cal=True):
        mean_k = np.zeros((self.k, self.d))
        for i, c in enumerate(self.clusters):
            class_data = self.data[self.labels == c]
            if len(class_data) == 0:
                mean_k[i] = self.mean_k[i]
                if print_cal:
                    print(f"Class {c} is empty; keeping previous centroid {mean_k[i]}")
            else:
                mean_k[i] = np.mean(class_data, axis=0)
                if print_cal:
                    print(f"Mean centroid for Class {c}: {mean_k[i]}")
        return mean_k


    def distortion_measure(self):
        """ Define the Objective function (distortion measure) J (9.1) PRML"""
        J = 0
        for i in range(self.n):
            for k in range(self.k):
                # Encodes the 1 of K encoding
                if self.labels[i] == self.clusters[k]:
                    diff = self.data[i] - self.mean_k[k]
                    J += np.dot(diff, diff)
        return J

    def update_labels(self):
        """ Assigns the i-th datapoint to the nearest centroid"""
        new_labels = np.zeros(self.n, dtype=int)
        for i in range(self.n):
            distances = np.zeros(self.k)
            for k in range(self.k):
                diff = self.data[i] - self.mean_k[k]
                distances[k] = np.dot(diff, diff)
            nearest_cluster = np.argmin(distances)
            new_labels[i] = self.clusters[nearest_cluster]

        changed = self.labels is None or not np.array_equal(new_labels, self.labels)
        self.labels = new_labels
        return changed

    def update_means(self):
        """ Update mean vectors for each class k (9.4) PRML"""
        self.mean_k = self.compute_mean_k()

    def optimize(self):
        """ Optimize the classifier using PRML algorithm."""
        for iteration in range(self.max_iters):
            print(f"Iteration {iteration + 1}")
            changed = self.update_labels()
            self.update_means()
            J = self.distortion_measure()
            print(f"Distortion measure J: {J}")
            if not changed:
                print("Convergence reached.")
                break

    def prediction_accuracy(self):
        """ Compute prediction accuracy if test labels are provided."""
        if self.test_labels is None:
            raise ValueError("Test labels not provided for accuracy computation.")
        pred = self.labels == self.test_labels
        accuracy = np.sum(pred) / self.n
        return accuracy
# Coordinates x,y
A = np.array([[3,8],
              [4,7],
              [3,6],
              [4,5],
              [5,5],
              [9,5],
              [3,4],
              [8,4],
              [5,1],
              [9,1]])

labels =[1,1,1,2,2,2,1,2,2,2] # 1 for light-blue, 2 for dark-blue

# I choose my guess for the initial means which decides the initial clusters to be labeled accordingly in
# update_labels()
initial_means = np.array([[4,4],
                          [7,2]])

kmeans = KMeansClassifier(data = A,
                          initial_means = initial_means,
                          test_labels=labels,
                          k = 2,
                          max_iters=100)
kmeans.optimize()
print("The classification accuracy is: ", kmeans.prediction_accuracy())

import pandas as pd

df = pd.DataFrame({
    "outlook": [
        "sunny", "sunny", "overcast", "rain", "rain", "rain",
        "overcast", "sunny", "sunny", "rain", "sunny",
        "overcast", "overcast", "rain"
    ],
    "temperature": [
        "hot", "hot", "hot", "mild", "cool", "cool",
        "cool", "mild", "cool", "mild", "mild",
        "mild", "hot", "mild"
    ],
    "humidity": [
        "high", "high", "high", "high", "normal", "normal",
        "normal", "high", "normal", "normal", "normal",
        "high", "normal", "high"
    ],
    "windy": [
        False, True, False, False, False, True,
        True, False, False, False, True,
        True, False, True
    ],
    "class": [
        "N", "N", "P", "P", "P", "N",
        "P", "N", "P", "P", "P",
        "P", "P", "N"
    ]
})

def entropy(df, col):
    """ Compute the entropy of the data """
    n = len(df)

    # Empty df
    p = dict()

    # N, P frequency by column value
    unique_values = df[col].unique()

    # If we want to compute the entropy of the class column, we can directly compute it
    # without grouping by the column values
    if col == "class":
        n = len(df)
        df = df["class"].value_counts()
        df["class"] = df.apply(lambda x: -x/n*np.log2(x/n))
        return df["class"].sum()


    for value in unique_values:
        # For each value compute:

        temp = df[df[col] == value][[col, "class"]]
        # How many of each class for the value
        temp = temp.groupby("class").count().reset_index()

        # Normalize by how many class instances there are for the value
        temp[col] = temp[col] / temp[col].sum()

        # Apply transformation to the column, -p*log2(p)
        temp[col] = temp[col].apply(lambda x: -x*np.log2(x))
        # Sum over the column, and store in dict
        p[value] = temp[col].sum()

    # Compute entropy
    return pd.DataFrame.from_dict(p, orient='index', columns=['entropy'])

def information_gain(df, col):
    """ Compute the information gain of the data """
    n = len(df)
    ig = entropy(df, "class")

    unique_values = df[col].unique()
    for value in unique_values:
        ig -= len(df[df[col] == value][[col, "class"]]) / n * entropy(df, col).loc[value]
    return ig.values[0]

print("Information Gain for humidity:", information_gain(df, "humidity"))
print("Information Gain for temperature:", information_gain(df, "temperature"))
print("Information Gain for wind:", information_gain(df, "windy"))
print("Information Gain for outlook:", information_gain(df, "outlook"))
print()
# Subset on outlook
df_new = df[df["outlook"] == "sunny"]
print("Sunny")
print("Information Gain for hum:", information_gain(df_new, "humidity"))
print("Information Gain for temp:", information_gain(df_new, "temperature"))
print("Information Gain for wind:", information_gain(df_new, "windy"))
print()
# Subset on outlook
df_new = df[df["outlook"] == "overcast"]
print("Overcast")
print("Information Gain for hum:", information_gain(df_new, "humidity"))
print("Information Gain for temp:", information_gain(df_new, "temperature"))
print("Information Gain for wind:", information_gain(df_new, "windy"))
# No more information gain, so we can stop here. The decision tree would be:
print("Class :", unique(df_new["class"])[0])
print()
# Subset on outlook
df_new = df[df["outlook"] == "rain"]
print("Rain")
print("Information Gain for hum:", information_gain(df_new, "humidity"))
print("Information Gain for temp:", information_gain(df_new, "temperature"))
print("Information Gain for wind:", information_gain(df_new, "windy"))
print()

#Subset on humidity and sunny
df_new = df[(df["outlook"] == "sunny") & (df["humidity"] == "high")]
print("Sunny -> Humidity -> High")
print("Information Gain for temp:", information_gain(df_new, "temperature"))
print("Information Gain for wind:", information_gain(df_new, "windy"))
# No more information gain, so we can stop here. The decision tree would be:
print("Class :", unique(df_new["class"])[0])
print()


#Subset on humidity and sunny
df_new = df[(df["outlook"] == "sunny") & (df["humidity"] == "normal")]
print("Sunny -> Humidity -> normal")
print("Information Gain for temp:", information_gain(df_new, "temperature"))
print("Information Gain for wind:", information_gain(df_new, "windy"))
# No more information gain, so we can stop here. The decision tree would be:
print("Class :", unique(df_new["class"])[0])
print()


#Subset on wind and rain
df_new = df[(df["outlook"] == "rain") & (df["windy"] == True)]
print("Sunny -> Humidity -> windy")
print("Information Gain for temp:", information_gain(df_new, "temperature"))
print("Information Gain for wind:", information_gain(df_new, "humidity"))
# No more information gain, so we can stop here. The decision tree would be:
print("Class :", unique(df_new["class"])[0])
print()

#Subset on wind and rain
df_new = df[(df["outlook"] == "rain") & (df["windy"] == False)]
print("Sunny -> Humidity -> windy")
print("Information Gain for temp:", information_gain(df_new, "temperature"))
print("Information Gain for wind:", information_gain(df_new, "humidity"))
# No more information gain, so we can stop here. The decision tree would be:
print("Class :", unique(df_new["class"])[0])
print()