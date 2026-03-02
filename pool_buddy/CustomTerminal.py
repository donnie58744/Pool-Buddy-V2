class PrintColor:
    @staticmethod
    def red(string): print("\033[91m{}\033[00m" .format(string))
    @staticmethod
    def green(string): print("\033[92m{}\033[00m" .format(string))
    @staticmethod
    def yellow(string): print("\033[93m{}\033[00m" .format(string))