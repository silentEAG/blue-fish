class Config(object):
    def __init__(self, save_path = "./", dist_dir = "data/dist", index_dir = "data/index", proxy: str = None, pull = "all", force = False):
        self.save_path = save_path
        self.dist_dir = dist_dir
        self.index_dir = index_dir
        self.proxy = proxy
        self.pull = pull
        self.force = force

    def merge(self, arg):
        if arg.pull:
            self.pull = arg.pull.split(",")
        if arg.force:
            self.force = arg.force
        if arg.proxy is not None:
            self.proxy = arg.proxy
        if arg.path is not None:
            if not arg.path.endswith("/"):
                arg.path += "/"
            self.save_path = arg.path
        pass


config = Config()
