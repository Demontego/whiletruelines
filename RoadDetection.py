import segmentation_models_pytorch as smp
import albumentations as album
import numpy as np
import cv2
import torch
import matplotlib.pyplot as plt
from pyproj import Proj, transform
from geojson import Polygon

class RoadDetection:
    """
    Model detect road on map and predict mask, heatmap of image
    """

    def __init__(self, path_model='./best_model_LinkNet34.pth', img_size=1024, device='cpu', enc=None, enc_w=None):
        """
        path_model - path to load model for inference,
        img_size - size of out image, mask and heatmap
        device - cpu or gpu
        enc - name encoder for preprocessing, check list on https://github.com/qubvel/segmentation_models.pytorch
        enc_w - name weight after train on dataset, check list on https://github.com/qubvel/segmentation_models.pytorch
        """
        self.model = torch.load(path_model, map_location=device)
        self.model.eval()
        self.select_classes = ['background', 'road']
        self.select_class_rgb_values = [[0, 0, 0], [255, 255, 255]]
        self.device = torch.device(device)
        if enc == None:
            enc = self.model.name[self.model.name.find('-')+1:]
        if enc_w == None:
            enc_w = 'imagenet'
        self.img_size = img_size
        self.polygon = Polygon
        self.UTM = Proj(init='EPSG:32637')
        self.WGS84 = Proj(init="EPSG:4326")
        self.preproc_vis = album.Resize(img_size, img_size)
        self.preprocessing = album.Compose([
            album.Resize(img_size, img_size),
            album.Lambda(image=smp.encoders.get_preprocessing_fn(enc, enc_w)),
            album.Lambda(image=self.to_tensor),
        ])

    def predict(self, image_path):
        """
        I want path of image
        """
        data_coord = []
        with open(image_path[:-3]+'tfw', "r") as fin:
            for line in fin.readlines():
                data_coord.append(float(line))
        img = cv2.cvtColor(cv2.imread(image_path),
                           cv2.COLOR_BGR2RGB).astype('uint8')
        orig_size = img.shape[0]
        img_vis = self.preproc_vis(image=img)['image']
        img = self.preprocessing(image=img)['image']
        x_tensor = torch.from_numpy(img).to(self.device).unsqueeze(0)
        pred_mask = self.model(x_tensor)
        pred_mask = pred_mask.detach().squeeze().cpu().numpy()
        pred_mask = np.transpose(pred_mask, (1, 2, 0))
        pred_road_heatmap = pred_mask[:, :, self.select_classes.index('road')]
        pred_mask = self.colour_code_segmentation(
            self.reverse_one_hot(pred_mask))
        img_vis = img_vis * (pred_mask == 0) + \
            (pred_mask // 255) * np.array([128, 0, 128])
        pred_mask = pred_mask[:, :, 0]
        thresh = cv2.inRange(pred_mask, 200, 255)
        contours, hierarchy = cv2.findContours(
            thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        polygons = []
        polygons_vis = []
        for mask2 in contours:
            if len(mask2) > 50:
                polygon = []
                polygon_vis = []
                for p in mask2[::4]:
                    new_x = data_coord[4]+data_coord[0] * \
                        orig_size/self.img_size*p[0, 0]
                    new_y = data_coord[5]+data_coord[3] * \
                        orig_size/self.img_size*p[0, 1]
                    polygon.append((new_x, new_y))
                    polygon_vis.append(transform(self.UTM, self.WGS84, new_x, new_y))
                polygon.append(polygon[0])
                polygon_vis.append(polygon_vis[0])
                polygons_vis.append(polygon_vis)
                polygons.append(polygon)
        geojson_data = self.polygon(polygons, precision=10)
        geojson_show = self.polygon(polygons_vis, precision=10)
        pred_road_heatmap = cv2.applyColorMap((pred_road_heatmap*255).astype(np.uint8), cv2.COLORMAP_HOT)
        return img_vis, pred_mask, pred_road_heatmap, geojson_data, geojson_show

    def reverse_one_hot(self, pred_mask):
        x = np.argmax(pred_mask, axis=-1)
        return x

    def colour_code_segmentation(self, image):
        colour_codes = np.array(self.select_class_rgb_values)
        x = colour_codes[image.astype(int)]
        return x

    def to_tensor(self, x, **kwargs):
        return x.transpose(2, 0, 1).astype('float32')