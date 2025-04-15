# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import itertools

from utils import FilePathBuilder, CONSTANTS


class BuildVectorWrapper:
    def __init__(self, benchmark, vector_builder, repos, window_sizes, slice_sizes):
        self.repos = repos
        self.window_sizes = window_sizes
        self.slice_sizes = slice_sizes
        self.vector_builder = vector_builder
        self.benchmark = benchmark

    def vectorize_repo_windows(self):
        for window_size, slice_size in itertools.product(self.window_sizes, self.slice_sizes):
            for repo in self.repos:
                builder = self.vector_builder(
                    FilePathBuilder.repo_windows_path(repo, window_size, slice_size)
                )
                builder.build()

    def vectorize_baseline_and_ground_windows(self):
        for window_size in self.window_sizes:
            for repo in self.repos:
                builder = self.vector_builder(
                    FilePathBuilder.search_first_window_path(
                        self.benchmark, CONSTANTS.rg, repo, window_size
                    )
                )
                builder.build()
                builder = self.vector_builder(
                    FilePathBuilder.search_first_window_path(
                        self.benchmark, CONSTANTS.gt, repo, window_size
                    )
                )
                builder.build()

    def vectorize_prediction_windows(self, mode, prediction_path_template):
        for window_size, slice_size in itertools.product(self.window_sizes, self.slice_sizes):
            prediction_path = prediction_path_template.format(
                window_size=window_size, slice_size=slice_size
            )
            for repo in self.repos:
                window_path = FilePathBuilder.gen_first_window_path(
                    self.benchmark, mode, prediction_path, repo, window_size
                )
                builder = self.vector_builder(window_path)
                builder.build()
