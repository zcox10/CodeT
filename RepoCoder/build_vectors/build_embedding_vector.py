from collections import defaultdict

from utils import Tools, FilePathBuilder


class BuildEmbeddingVector:
    """
    utilize external embedding model to generate embedding vector
    """

    def __init__(self, repos, window_sizes, slice_sizes):
        self.repos = repos
        self.window_sizes = window_sizes
        self.slice_sizes = slice_sizes

    def build_input_file_for_repo_window(self, slice_size):
        lines = []
        for window_size in self.window_sizes:
            for repo in self.repos:
                file_path = FilePathBuilder.repo_windows_path(repo, window_size, slice_size)
                loaded_lines = Tools.load_pickle(file_path)
                for line in loaded_lines:
                    lines.append(
                        {
                            "context": line["context"],
                            "metadata": {
                                "window_file_path": file_path,
                                "original_metadata": line["metadata"],
                            },
                        }
                    )
        return lines

    def build_input_file_search_first_window(self, mode, benchmark):
        lines = []
        for window_size in self.window_sizes:
            for repo in self.repos:
                file_path = FilePathBuilder.search_first_window_path(
                    benchmark, mode, repo, window_size
                )
                loaded_lines = Tools.load_pickle(file_path)
                for line in loaded_lines:
                    lines.append(
                        {
                            "context": line["context"],
                            "metadata": {
                                "window_file_path": file_path,
                                "original_metadata": line["metadata"],
                            },
                        }
                    )
        return lines

    def build_input_file_for_gen_first_window(self, mode, benchmark, prediction_path):
        lines = []
        for window_size in self.window_sizes:
            for repo in self.repos:
                file_path = FilePathBuilder.gen_first_window_path(
                    benchmark, mode, prediction_path, repo, window_size
                )
                loaded_lines = Tools.load_pickle(file_path)
                for line in loaded_lines:
                    lines.append(
                        {
                            "context": line["context"],
                            "metadata": {
                                "window_file_path": file_path,
                                "original_metadata": line["metadata"],
                            },
                        }
                    )
        return lines

    @staticmethod
    def place_generated_embeddings(generated_embeddings):
        vector_file_path_to_lines = defaultdict(list)
        for line in generated_embeddings:
            window_path = line["metadata"]["window_file_path"]
            original_metadata = line["metadata"]["original_metadata"]
            vector_file_path = FilePathBuilder.ada002_vector_path(window_path)
            vector_file_path_to_lines[vector_file_path].append(
                {"context": line["context"], "metadata": original_metadata, "data": line["data"]}
            )
        for vector_file_path, lines in vector_file_path_to_lines.items():
            Tools.dump_pickle(lines, vector_file_path)
