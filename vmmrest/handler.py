import os
from VirtualMailManager.config import Config as Cfg
from VirtualMailManager.errors import NotRootError
from VirtualMailManager import handler

# monkey-patch config search paths
handler.CFG_PATH = ':'.join([
    os.path.join(os.path.expanduser('~'), '.config', 'vmm'),
    handler.CFG_PATH
])


class RestHandler(handler.Handler):
    def __init__(self):
        try:
            super().__init__(skip_some_checks=True)
        except NotRootError:
            # we don’t care, but do everything that super().__init__ would have
            # done hadn’t it thrown the exception.
            # TODO: maybe implement something like skip_root_check keyword-arg in Handler?
            if self._check_cfg_file():
                self._cfg = Cfg(self._cfg_fname)
                self._cfg.load()
        self.cfg_install()
