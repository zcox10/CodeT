# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import itertools
import functools

from utils import Tools, FilePathBuilder, CONSTANTS
from make_windows.baseline_window_maker import BaselineWindowMaker
from make_windows.ground_truth_window_maker import GroundTruthWindowMaker
from make_windows.prediction_window_maker import PredictionWindowMaker
from make_windows.repo_window_maker import RepoWindowMaker

from collections import defaultdict
import os


class MakeWindowWrapper:
    def __init__(self, benchmark, repos, window_sizes, slice_sizes):
        self.repos = repos
        self.window_sizes = window_sizes
        self.slice_sizes = slice_sizes

        self.benchmark = benchmark

        if benchmark == CONSTANTS.line_benchmark:
            self.task_file_path = FilePathBuilder.random_line_completion_benchmark
        elif benchmark == CONSTANTS.api_benchmark:
            self.task_file_path = FilePathBuilder.api_completion_benchmark
        elif benchmark == CONSTANTS.short_line_benchmark:
            self.task_file_path = FilePathBuilder.short_random_line_completion_benchmark
        elif benchmark == CONSTANTS.short_api_benchmark:
            self.task_file_path = FilePathBuilder.short_api_completion_benchmark

    def window_for_repo_files(self):
        for window_size, slice_size in itertools.product(self.window_sizes, self.slice_sizes):
            for repo in self.repos:
                repo_window_maker = RepoWindowMaker(repo, window_size, slice_size)
                repo_window_maker.build_windows()

    def window_for_baseline_and_ground(self):
        tasks = Tools.load_jsonl(self.task_file_path)

        for window_size in self.window_sizes:
            for repo in self.repos:
                baseline_window_maker = BaselineWindowMaker(
                    self.benchmark, repo, window_size, tasks
                )
                ground_window_maker = GroundTruthWindowMaker(
                    self.benchmark, repo, window_size, tasks
                )
                baseline_window_maker.build_window()
                ground_window_maker.build_window()

    def window_for_prediction(self, mode, prediction_path_template):
        for window_size, slice_size in itertools.product(self.window_sizes, self.slice_sizes):
            prediction_path = prediction_path_template.format(
                window_size=window_size, slice_size=slice_size
            )
            for repo in self.repos:
                window_path_builder = functools.partial(
                    FilePathBuilder.gen_first_window_path, self.benchmark, mode
                )
                pred_window_maker = PredictionWindowMaker(
                    repo, window_size, prediction_path, window_path_builder
                )
                pred_window_maker.build_window()
