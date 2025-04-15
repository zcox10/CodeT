import tqdm
from concurrent.futures import as_completed, ProcessPoolExecutor

from utils import Tools, FilePathBuilder


class BagOfWords:
    def __init__(self, input_file):
        self.input_file = input_file

    def build(self):
        print(f"building one gram vector for {self.input_file}")
        futures = dict()
        lines = Tools.load_pickle(self.input_file)
        with ProcessPoolExecutor(max_workers=48) as executor:
            for line in lines:
                futures[executor.submit(Tools.tokenize, line["context"])] = line

            new_lines = []
            t = tqdm.tqdm(total=len(futures))
            for future in as_completed(futures):
                line = futures[future]
                tokenized = future.result()
                new_lines.append(
                    {
                        "context": line["context"],
                        "metadata": line["metadata"],
                        "data": [{"embedding": tokenized}],
                    }
                )
                tqdm.tqdm.update(t)
            output_file_path = FilePathBuilder.one_gram_vector_path(self.input_file)
            Tools.dump_pickle(new_lines, output_file_path)
