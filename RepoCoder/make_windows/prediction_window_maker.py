from utils import Tools


class PredictionWindowMaker:
    def __init__(self, repo, window_size, prediction_path, window_path_builder):
        self.repo = repo
        self.window_size = window_size
        self.prediction_path = prediction_path
        self.source_code = Tools.iterate_repository(repo)
        self.predictions = Tools.load_jsonl(prediction_path)
        self.window_path_builder = window_path_builder

    def build_window(self, type="centered"):
        code_windows = []
        delta_size = self.window_size // 2
        for prediction in self.predictions:
            if prediction["metadata"]["task_id"].split("/")[0] != self.repo:
                continue
            fpath_tuple = tuple(prediction["metadata"]["fpath_tuple"])
            line_no = prediction["metadata"]["line_no"]  # line_no in prediction file starts from 0
            original_code = self.source_code[fpath_tuple]
            code_lines = original_code.splitlines()
            context_start_lineno = prediction["metadata"]["context_start_lineno"]
            start_line_no = max(context_start_lineno, line_no - delta_size)
            for sample in [
                prediction["choices"][i]["text"] for i in range(len(prediction["choices"]))
            ]:
                # TODO actually only one sample is generated
                sample_lines = [i for i in sample.splitlines() if i.strip()]
                new_code_lines = code_lines[:line_no] + sample_lines
                end_line_no = min(len(new_code_lines), line_no + self.window_size - delta_size)
                window_lines = [i for i in new_code_lines[start_line_no:end_line_no] if i.strip()]
                if not window_lines:  # all empty lines
                    continue
                code_windows.append(
                    {
                        "context": "\n".join(window_lines),
                        "metadata": {
                            "fpath_tuple": fpath_tuple,
                            "line_no": line_no,  # line_no starts from 0
                            "prediction": sample,
                            "task_id": prediction["metadata"]["task_id"],
                            "start_line_no": start_line_no,
                            "end_line_no": end_line_no,
                            "window_size": self.window_size,
                            "context_start_lineno": context_start_lineno,
                            "repo": self.repo,
                        },
                    }
                )
        print(
            f"build {len(code_windows)} prediction windows for {self.repo} with window size {self.window_size}"
        )
        output_path = self.window_path_builder(self.prediction_path, self.repo, self.window_size)
        Tools.dump_pickle(code_windows, output_path)
