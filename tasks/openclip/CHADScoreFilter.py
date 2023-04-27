import clip as _clip
import numpy as _numpy
import torch as _torch
import torch.nn as _torch_nn

import utils
from tasks import FkReportableTask as _FkReportableTask, FkImage


class _AestheticPredictor(_torch_nn.Module):
    def __init__(self, input_size):
        super().__init__()
        self.input_size = input_size
        self.layers = _torch_nn.Sequential(
            _torch_nn.Linear(self.input_size, 1024),
            _torch_nn.Dropout(0.2),
            _torch_nn.Linear(1024, 128),
            _torch_nn.Dropout(0.2),
            _torch_nn.Linear(128, 64),
            _torch_nn.Dropout(0.1),
            _torch_nn.Linear(64, 16),
            _torch_nn.Linear(16, 1),
        )

    def forward(self, x):
        return self.layers(x)


class CHADScoreFilter(_FkReportableTask):

    def __init__(self, score_threshold: float):
        self.score_threshold = score_threshold

        self._scorer_name = "chadscorer.pth"
        self._device = "cuda:0" if _torch.cuda.is_available() else "cpu"
        self._pt_state = _torch.load(self._scorer_name, map_location=_torch.device("cpu"))

        self._chad_predictor = _AestheticPredictor(768)
        self._chad_predictor.load_state_dict(self._pt_state)
        self._chad_predictor.to(self._device)
        self._chad_predictor.eval()

        self._chad_scores = []

        clip_model, clip_preprocess = _clip.load("ViT-L/14", device=self._device)

        print(f"Chad scorer using device: {self._device}")

        self._clip_model = clip_model
        self._clip_preprocess = clip_preprocess

    def process(self, image: FkImage) -> bool:
        chad_resized_image = utils.resize_image_aspect(image.image, 768)  # is a resize even need to help
        # the memory balloon? needs moar testing

        chad_image = self._clip_preprocess(chad_resized_image).unsqueeze(0).to(self._device)

        with _torch.no_grad():
            image_features1 = self._clip_model.encode_image(chad_image)
            image_features = image_features1 / image_features1.norm(dim=-1, keepdim=True)

        del image_features1

        image_features = image_features.cpu().detach().numpy()
        t_features = _torch.from_numpy(image_features).to(self._device).float()

        score_iter = self._chad_predictor(t_features)
        score = score_iter.item()

        # score_iter = None
        # image_features = None
        # t_features = None
        # chad_image = None

        chad_resized_image.close()
        del chad_resized_image

        del score_iter
        del chad_image
        del image_features
        del t_features

        self._chad_scores.append(score)
        return score >= self.score_threshold

    def report(self) -> list[tuple[str, any]]:
        return [
            ("Filter Threshold", self.score_threshold),
            None,
            ("Average CHAD Score", _numpy.mean(self._chad_scores)),
            ("90th Percentile", _numpy.percentile(self._chad_scores, 90))
        ]
