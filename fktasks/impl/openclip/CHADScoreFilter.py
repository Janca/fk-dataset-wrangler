import argparse as _argparse
import os as _os

import clip as _clip
import numpy as _numpy
import torch as _torch
import torch.nn as _torch_nn

import utils
from fktasks import FkReportableTask as _FkReportableTask, FkImage as _FkImage, \
    FkTaskIntensiveness as _FkTaskIntensiveness


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

    def __init__(self, score_threshold: float = -1):
        self._clip_preprocess = None
        self._clip_model = None
        self._chad_scores = None
        self._chad_predictor = None
        self._pt_state = None
        self._device = None
        self.score_threshold = score_threshold

    def initialize(self):
        scoring_model_path = "models/chadscorer.pth"

        if not _os.path.exists(scoring_model_path):
            print("Downloading scoring model:", scoring_model_path)
            utils.download_file(
                "https://github.com/grexzen/SD-Chad/blob/main/chadscorer.pth?raw=true",
                scoring_model_path
            )

        self._device = "cuda" if _torch.cuda.is_available() else "cpu"
        self._pt_state = _torch.load(scoring_model_path, map_location=_torch.device("cpu"))

        self._chad_predictor = _AestheticPredictor(768)
        self._chad_predictor.load_state_dict(self._pt_state)
        self._chad_predictor.to(self._device)
        self._chad_predictor.eval()

        self._chad_scores = []

        vit_model_name = "ViT-L-14"
        if not _os.path.exists(f"models/{vit_model_name}.pt"):
            print("Downloading ViT-L/14")

        clip_model, clip_preprocess = _clip.load("ViT-L/14", device=self._device, download_root="models")

        print(f"Chad scorer using device: {self._device}")

        self._clip_model = clip_model
        self._clip_preprocess = clip_preprocess

    def register_args(self, arg_parser: _argparse.ArgumentParser):
        arg_parser.add_argument(
            "--chad-score",
            default=-1,
            type=float,
            help="discard image if image does not meet aesthetic score "
                 "(0 - 8; 0 = least aesthetic; 8 = most aesthetic; default: -1 [disabled])"
        )

    def parse_args(self, args: _argparse.Namespace) -> bool:
        self.score_threshold = args.chad_score
        return self.score_threshold >= 0

    def process(self, image: _FkImage) -> bool:
        chad_image = self._clip_preprocess(image.image).unsqueeze(0).to(self._device)

        with _torch.inference_mode():
            image_features1 = self._clip_model.encode_image(chad_image)
            image_features = image_features1 / image_features1.norm(dim=-1, keepdim=True)

        del image_features1

        image_features = image_features.cpu().detach().numpy()
        t_features = _torch.from_numpy(image_features).to(self._device).float()

        score_iter = self._chad_predictor(t_features)
        _torch.cuda.synchronize()

        score = score_iter.item()

        # score_iter = None
        # image_features = None
        # t_features = None
        # chad_image = None

        del score_iter
        del chad_image
        del image_features
        del t_features

        self._chad_scores.append(score)
        return score >= self.score_threshold

    @property
    def priority(self) -> int:
        return 100_000

    @property
    def intensiveness(self) -> _FkTaskIntensiveness:
        return _FkTaskIntensiveness.GPU

    def report(self) -> list[tuple[str, any]]:
        return [
            ("Filter Threshold", self.score_threshold),
            None,
            ("Average CHAD Score", utils.safe_fn(lambda: _numpy.mean(self._chad_scores), -1)),
            ("90th Percentile", utils.safe_fn(lambda: _numpy.percentile(self._chad_scores, 90), -1))
        ]

    @classmethod
    def webui_config(cls, *args, **kwargs):
        # TODO: Implement actual config UI
        pass

    @classmethod
    def webui_validate(cls, *args, **kwargs) -> bool:
        # TODO: Implement actual validation logic
        return True

    @classmethod
    def webui_info(cls, *args, **kwargs):
        # TODO: Implement actual info display logic
        pass
