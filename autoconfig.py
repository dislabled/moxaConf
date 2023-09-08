#!/usr/bin/env python3
# coding=utf-8


from csv import DictReader, DictWriter

class ConfigFile():
    def __init__(self) -> None:
        pass

    def read_config(self, file:str) -> list:
        """ Read CSV file and output dictionary
            Header - Cabinet,AP,SW,IOG,MBB,DIPB,MBR,DIPR,IBC IP address,
                     Switch IP address,Position,MAC M,MAC R
            input:
                csvfile (str)
            Outputs:
                parsed dictionary(list)
        """
        with open(file, 'r') as f:
            config = list(DictReader(f, delimiter=',', quotechar='"'))
        return config

    def write_config(self, file:str, cabinet:str, mac:str, main:bool) -> None:
        """ Write the MAC address to the csv file

            input:
                file(str)
                cabinet(str) row to change
                mac(str) MAC to add row
                main(bool) Main or Reserve Mac to add
        """
        print(file)
        print(cabinet)
        print(mac)
        print(main)

        with open(file, 'r+') as f:
            csvobject = DictReader(f, delimiter=',', quotechar='"')
            csvlist = list(csvobject)
            for row in csvlist:
                if row['Cabinet'] == cabinet:
                    print('found in list')
                    if main:
                        row['MAC M'] = mac
                        print(row)

            f.seek(0)
            data = DictWriter(f, delimiter=',',
                              quotechar='"', fieldnames=csvobject.fieldnames)
            data.writeheader()
            data.writerows(csvlist)

class AutoConfig():
    """ Configures switch according to configfile and connected ports
    """
    def __init__(self) -> None:
        pass

    def update_switch(self):
        # Main or reserve:
            # Set Cabinet + M/R
            # Set Location
            # Set ipaddress
            # Check connected ports
            #   - set alarm on connected ports
        pass

if __name__ == "__main__":

    test = ConfigFile()
    # configlist = test.read_config('config.test.csv')
    test.write_config('site/config.test.csv', 'AP19', 'testmac', True)
    # configlist = read_config('config.csv')
    # for number, line in enumerate(configlist):
    #     print(f'{number}:  {line["Position"]}')
    input()

