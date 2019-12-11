class EDRContracts(object):

    def __init__(self, max_nb, contracts=[]):
        self.max_nb = max_nb
        self.contracts = { c["cname"] : c["reward"] for c in contracts }

    def contract(self, cmdr_name):
        if not cmdr_name:
            return None
        return self.contracts.get(cmdr_name.lower(), None)

    def place_reward(self, cmdr_name, reward):
        if not cmdr_name:
            return False
        if cmdr_name.lower() in self.contracts:
            self.contracts[cmdr_name.lower()] = reward
        elif len(self.contracts) >= self.max_nb:
            return False
        
        self.contracts[cmdr_name.lower()] = reward
        return True