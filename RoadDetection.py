import segmentation_models_pytorch as smp
import albumentations as album
import numpy as np
import cv2
import torch


class RoadDetection:
    """
    Model detect road on map and predict mask, heatmap of image
    """

    def __init__(self, path_model='./best_model_LinkNet34.pth', img_size=4096, device='cpu', enc=None, enc_w=None):
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
        img = cv2.cvtColor(cv2.imread(image_path),
                           cv2.COLOR_BGR2RGB).astype('uint8')
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
        return img_vis, pred_mask, (pred_road_heatmap*255).astype(int)

    def reverse_one_hot(self, pred_mask):
        x = np.argmax(pred_mask, axis=-1)
        return x

    def colour_code_segmentation(self, image):
        colour_codes = np.array(self.select_class_rgb_values)
        x = colour_codes[image.astype(int)]
        return x

    def to_tensor(self, x, **kwargs):
        return x.transpose(2, 0, 1).astype('float32')