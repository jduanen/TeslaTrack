'''
################################################################################
#
# TeslaTrack interactive command interpreter object
#
################################################################################
'''

class CommandInterpreter():
    ''' #### FIXME
    '''
    def __init__(self, prompt="> "):
        self.prompt = prompt
        self.cmd = ""

    def run(self):
        while True:
            line = input(self.prompt)
            words = line.split(' ')
            cmd = words[0].lower().strip()
            args = words[1:]
            if cmd == 'a':
                print(f"????")
            if cmd == 'b':
                pass
            if cmd == 'c':
                pass
            elif cmd == 'q':
                print("Exiting...")
                break
            elif cmd == '?' or cmd == 'h':
                print("Help:")
                print("    h: print this help message")
                print("    a: ????")
                print("    q: quit")
                print("    ?: print this help message")
        logging.info("commandInterpreter: exiting")

