# a data structure for device specific information
class DeviceInfo(object):
    def __init__(self):
        self.machine = ""
        self.arch = ""
        self.osname = ""
        self.name = ""
        self.dist = ""
        self.uuid = ""

    def get_info(self):
        """
        Prepare a dictionary of data member in sequence.
        1. Machine 
        2. Architecture
        3. Operating system
        4. Machine name 
        5. Operating system distrubution
        6. UUID
        Parameters
        ----------
        self :
            return a dictionary of data members
        """

        data_lst = {
            "uuid": self.uuid,
            "machine": self.machine,
            "arch": self.arch,
            "os": self.osname,
            "device": self.machine,
            "os distribution": self.dist
        }
        return data_lst


class ARMDevice(DeviceInfo):
    def __init__(self):
        DeviceInfo.__init__(self)
        self.processor = ""
        self.speed = ""
        self.arch = ""

    def get_info(self):
        """
        Prepare a dictionary of data member in sequence.
        1. Processor 
        2. Speed 
        3. Arch 
        Parameters
        ----------
        self :
            return a dictionary of data members
        """
        arm_data_lst = {
            "processor": self.processor,
            "speed": self.speed,
            "arch": self.arch
        }

        return arm_data_lst