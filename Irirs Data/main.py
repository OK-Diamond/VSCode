if __name__ == "__main__":
  
  import numpy as np
  import utilities as ut
  import matplotlib.pyplot as plt  
  from matplotlib.colors import ListedColormap
  
  cmap = ListedColormap(["#FF0000", "#00FF00", "#0000FF"])

  y_test = ut.readList("Iris_Test_Labels.txt")
  y_train = ut.readList("Iris_Training_Labels.txt")
  X_test = ut.readArray("Iris_Test_Data.txt")
  X_train = ut.readArray("Iris_Training_Data.txt")

  plt.figure()
  plt.scatter(X_train[:, 0], X_train[:, 1], c=y_train, cmap=cmap, edgecolor='k', s=20)
  plt.show()
