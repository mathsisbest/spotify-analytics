"""
Training pipeline for Spotify analytics ML models.

Usage:
    python -m ml.train --mode cluster
    python -m ml.train --mode predict
    python -m ml.train --mode forecast
"""

import argparse


def train_cluster() -> None: ...


def train_predict() -> None: ...


def train_forecast() -> None: ...


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, choices=["cluster", "predict", "forecast"])
    args = parser.parse_args()

    if args.mode == "cluster":
        train_cluster()
    elif args.mode == "predict":
        train_predict()
    elif args.mode == "forecast":
        train_forecast()
