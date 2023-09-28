from modules.callback import callbacks_list
from modules.data import UCF11DataModule
from modules.model import LitModel
from models import VGG19

from argparse import ArgumentParser
import os

from rich import print, traceback
traceback.install()

from lightning.pytorch import Trainer, seed_everything
import torch.optim as optim
import torch.nn as nn
import torch



# Set seed
seed_everything(seed=42, workers=True)

# Set number of worker (CPU will be used | Default: 60%)
NUM_WOKER = int(os.cpu_count()*0.6) if torch.cuda.is_available() else 0


def main(args):
    # Define dataset
    dataset = UCF11DataModule(
        data_path="data/UCF11", 
        sampling_value=3,
        batch_size=args.batch,
        num_workers=NUM_WOKER
    )

    # Define model
    model = VGG19(num_classes=11, hidden_features=256)
    lit_model = LitModel(
        model = model,
        criterion = nn.CrossEntropyLoss(),
        optimizer = optim.AdamW(model.parameters(), lr=args.learning_rate),
        checkpoint = None
    )

    # Define trainer
    trainer = Trainer(
        max_epochs=args.epoch, 
        precision="16-mixed",
        callbacks=callbacks_list
    )

    # Training
    trainer.fit(lit_model, dataset)

    # Testing
    trainer.test(lit_model, dataset)



if __name__=="__main__":
    parser = ArgumentParser()
    parser.add_argument("-e", "--epoch", type=int, default=-1)
    parser.add_argument("-b", "--batch", type=int, default=None)
    parser.add_argument("-lr", "--learning_rate", type=float, default=None)
    parser.add_argument("-cp", "--checkpoint", type=str, default=None)
    args = parser.parse_args()

    main(args)
