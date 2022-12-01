# SAE
Code and datasets for paper, Snowed Autoencoders Are Efficient Snow Removers

# The proposed labels
The labels of CSD, Snow-100K, and SRRS can be downloaded at https://drive.google.com/drive/folders/1fXiPOIh2K99kTqlhOpqvWkXg5Vwx0dt8?usp=sharing
The format of these csv files is
|        | name  | masks number|points|
|  ----  | ----  |----  |----  |
| 1083  | 7719.tif |1083|[[4, 0, 7, 0, 4, 3, 7, 3], [10, 0, 13, 0, 10, 3, 13, 3],...[286, 510, 289, 510, 286, 513, 289, 513]]|
| ... | ... | ... | ... |


The first column is a placeholder of the same value as the masks number.The second column shows the names of the image files in these datasets. The third column shows the number of snow particle masks in this image. The fourth column shows the coordinates of the four points of each mask. The format of these coordinates is [lower left x, lower left y, lower right x, lower right y, upper left x, upper left y, upper right x, upper right y].
