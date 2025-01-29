import pytorch_lightning as pl
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image
from torch import device

from .utils import list_to_str

# @TODO: Fix path for windows and local development / make it configurable
CHECKPOINT_PATH = "./solidarityzone/data/captcha_model.ckpt"
HEIGHT = 30
WIDTH = 100
CLASS_NUM = 10
CHAR_LEN = 5

transform = transforms.Compose(
    [
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ]
)


class CaptchaModel(pl.LightningModule):
    def __init__(self, model):
        super(CaptchaModel, self).__init__()
        self.model = model

    def forward(self, x):
        x = self.model(x)
        return x


class ModelConv(nn.Module):
    def __init__(self):
        super().__init__()
        self.layer1 = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )
        self.layer2 = nn.Sequential(
            nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )
        self.layer3 = nn.Sequential(
            nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )
        self.fc = nn.Sequential(
            nn.Linear(128 * (WIDTH // 8) * (HEIGHT // 8), 1024),
            nn.ReLU(),
            nn.Linear(1024, CLASS_NUM * CHAR_LEN),
        )

    def forward(self, x):
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        x = x.view(x.size(0), CHAR_LEN, CLASS_NUM)
        return x


def solve_captcha(image_path):
    model = CaptchaModel.load_from_checkpoint(
        CHECKPOINT_PATH, map_location=device("cpu"), model=ModelConv()
    ).to("cpu")
    model.eval()

    img = transform(Image.open(image_path))
    img = img.unsqueeze(0)
    y = model(img)
    y = y.permute(1, 0, 2)
    pred = y.argmax(dim=2)

    ans = list_to_str(pred)
    return ans
