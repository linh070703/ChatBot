import os
os.environ['HUGGINGFACE_HUB_CACHE'] = '/media/saplab/Data_Win/jh/hf_home/'

from huggingface_hub import snapshot_download
from tqdm import tqdm

import huggingface_hub 
huggingface_hub.__version__

def downloads(name:str):
#     ! mkdir -p "/media/saplab/Data_Win/jh/models/$name"
    snapshot_download(
        repo_id=name,
        ignore_patterns="*.pt",
#         local_dir="/media/saplab/Data_Win/jh/models/" + name,
#         local_dir_use_symlinks=False
    )

# downloads("NlpHUST/gpt-neo-vi-small")
# downloads("NlpHUST/gpt2-vietnamese")
# downloads("VietAI/gpt-neo-1.3B-vietnamese-news")
# downloads("VietAI/gpt-j-6B-vietnamese-news")

# downloads("bigscience/mt0-xxl-mt")
downloads("bigscience/mt0-small")
downloads("bigscience/mt0-base")
downloads("bigscience/mt0-large")
# downloads("bigscience/mt0-xl")
downloads("bigscience/bloomz-560m")
downloads("bigscience/bloomz-1b1")
downloads("bigscience/bloomz-1b7")
downloads("bigscience/bloomz-3b")