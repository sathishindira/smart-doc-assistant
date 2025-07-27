# Import libraries and setup
import os
import sys
import tempfile
import subprocess
import traceback
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Create working directory
work_dir = Path('/kaggle/working')
work_dir.mkdir(exist_ok=True)
os.chdir(work_dir)

print('Setup complete!')