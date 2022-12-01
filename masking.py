import cv2
import os, glob
import scipy.ndimage as ndimage
import scipy.spatial as spatial
import scipy.misc as misc
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import imageio
import pandas as pd
from natsort import natsorted
import warnings
warnings.filterwarnings("ignore",category=DeprecationWarning)

def create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)
    else:
        pass

def create_exp_folder():
    path_file_number = glob.glob(pathname='experiment/exp*')
    if len(path_file_number) == 0:
        create_folder('experiment/exp0')
        path_file_number = glob.glob(pathname='experiment/exp*')
    nums = [item[14:] for item in path_file_number]
    if len(glob.glob(pathname='experiment/exp{}/*'.format(max(nums)))) == 0:
        maxexp = max(nums)
        create_folder('experiment/exp{}'.format(maxexp))
    else:
        maxexp = max(nums)+1
        create_folder('experiment/exp{}'.format(maxexp))
    return ('experiment/exp{}'.format(maxexp))


class BBox(object):
    def __init__(self, x1, y1, x2, y2):
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
    def diagonal(self):
        return self.x2 - self.x1 + self.y2 - self.y1
    def overlaps(self, other):
        return not ((self.x1 > other.x2)
                    or (self.x2 < other.x1)
                    or (self.y1 > other.y2)
                    or (self.y2 < other.y1))
    def __eq__(self, other):
        return (self.x1 == other.x1
                and self.y1 == other.y1
                and self.x2 == other.x2
                and self.y2 == other.y2)

def find_paws(data, smooth_radius = 5, threshold = 0.0001):
    data = ndimage.uniform_filter(data, smooth_radius)
    thresh = data > threshold
    filled = ndimage.morphology.binary_fill_holes(thresh)
    coded_paws, num_paws = ndimage.label(filled)
    data_slices = ndimage.find_objects(coded_paws)
    return data_slices

def slice_to_bbox(slices):
    for s in slices:
        dy, dx = s[:2]
        yield BBox(dx.start, dy.start, dx.stop+1, dy.stop+1)

def remove_overlaps(bboxes):
    corners = []
    ulcorners = []
    bbox_map = {}

    for bbox in bboxes:
        ul = (bbox.x1, bbox.y1)
        lr = (bbox.x2, bbox.y2)
        bbox_map[ul] = bbox
        bbox_map[lr] = bbox
        ulcorners.append(ul)
        corners.append(ul)
        corners.append(lr)

    tree = spatial.KDTree(corners)
    for corner in ulcorners:
        bbox = bbox_map[corner]
        indices = tree.query_ball_point(
            corner, bbox_map[corner].diagonal(), p = 1)
        for near_corner in tree.data[indices]:
            near_bbox = bbox_map[tuple(near_corner)]
            if bbox != near_bbox and bbox.overlaps(near_bbox):
                bbox.x1 = near_bbox.x1 = min(bbox.x1, near_bbox.x1)
                bbox.y1 = near_bbox.y1 = min(bbox.y1, near_bbox.y1)
                bbox.x2 = near_bbox.x2 = max(bbox.x2, near_bbox.x2)
                bbox.y2 = near_bbox.y2 = max(bbox.y2, near_bbox.y2)
    return set(bbox_map.values())

if __name__ == '__main__':
    datasetpaths = ['/home/masters/liuyifan2/project/dataset/CSD/Train/Mask/',
                    '/home/masters/liuyifan2/project/dataset/CSD/Test/Mask/',
                    '/home/masters/liuyifan2/project/dataset/SRRS-2021/Combine Snow/',
                    '/home/masters/liuyifan2/project/dataset/all/mask/',
                    '/home/masters/liuyifan2/project/dataset/media/jdway/GameSSD/overlapping/test/Snow100K-L/mask/',
                    '/home/masters/liuyifan2/project/dataset/media/jdway/GameSSD/overlapping/test/Snow100K-M/mask/,'
                    '/home/masters/liuyifan2/project/dataset/media/jdway/GameSSD/overlapping/test/Snow100K-S/mask/']
    for datasetpath in datasetpaths:
        result = pd.DataFrame(columns=('name','masks number','points'))
        snowy_image = natsorted(os.listdir(datasetpath))

        for img_name in snowy_image:
            img_path = datasetpath + img_name
            print(img_path)
            img = cv2.imread(img_path)
            ret1, img1 = cv2.threshold(img, 63, 255, cv2.THRESH_BINARY)
            resized = cv2.resize(img1, (512, 512), interpolation=cv2.INTER_AREA)
            cv2.imwrite('masknor.png', resized)
            data = imageio.imread('masknor.png')
            data_slices = find_paws(data, smooth_radius = 0, threshold = 0.0001)
            bboxes = slice_to_bbox(data_slices)
            points = []
            i=0
            for bbox in bboxes:
                i+=1
                points.append([bbox.x1, bbox.y1,
                               bbox.x2, bbox.y1,
                               bbox.x1, bbox.y2,
                               bbox.x2, bbox.y2])
            df = [img_name, i, points]
            result.loc[i] = df
        result.to_csv('{}.csv'.format(datasetpath.split('/')[-3]+datasetpath.split('/')[-2]+datasetpath.split('/')[-1]))