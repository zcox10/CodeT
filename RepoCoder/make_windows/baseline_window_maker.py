from utils import Tools, FilePathBuilder, CONSTANTS


class BaselineWindowMaker:
    """the retrieve-and-generate approach"""

    def __init__(self, benchmark, repo, window_size, tasks):
        self.benchmark = benchmark
        self.repo = repo
        self.window_size = window_size
        self.tasks = tasks
        self.source_code = Tools.iterate_repository(repo)

    def build_window(self, print_lines=False):
        code_windows = []
        for task in self.tasks:
            if task["metadata"]["task_id"].split("/")[0] != self.repo:
                continue
            fpath_tuple = tuple(task["metadata"]["fpath_tuple"])
            line_no = task["metadata"]["line_no"]
            original_code = self.source_code[fpath_tuple]
            code_lines = original_code.splitlines()
            context_start_lineno = task["metadata"]["context_start_lineno"]
            start_line_no = max(context_start_lineno, line_no - self.window_size)
            window_lines = [i for i in code_lines[start_line_no:line_no]]
            code_windows.append(
                {
                    "context": "\n".join(window_lines),
                    "metadata": {
                        "fpath_tuple": fpath_tuple,
                        "line_no": line_no,  # line_no starts from 0
                        "task_id": task["metadata"]["task_id"],
                        "start_line_no": start_line_no,
                        "end_line_no": line_no,
                        "window_size": self.window_size,
                        "context_start_lineno": context_start_lineno,
                        "repo": self.repo,
                    },
                }
            )
            if print_lines:
                print("\nBASELINE:")
                print(f"START LINE: {start_line_no}")
                print(f"END LINE: {start_line_no}")
        print(
            f"build {len(code_windows)} baseline windows for {self.repo} with window size {self.window_size}"
        )
        output_path = FilePathBuilder.search_first_window_path(
            self.benchmark, CONSTANTS.rg, self.repo, self.window_size
        )
        Tools.dump_pickle(code_windows, output_path)
