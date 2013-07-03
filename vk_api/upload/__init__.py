import sys
if sys.version_info[0] == 2:
    from vk_upload import *
else:
    from .vk_upload import *
