from VirtualMailManager.handler import Handler


class RestHandler(Handler):
    def __init__(self):
        super().__init__(skip_root_check=True, skip_some_checks=True)
        self.cfg_install()
