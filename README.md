tdtool
======

tdtool.py fork from telldus/telldus with sensor support
Usage: ./tdtool.py [ options ]

Options:
         -[lsnfdbvh] [ --list ] [ --help ]
                      [ --sensor sensor ]
                      [ --on device ] [ --off device ] [ --bell device ]
                      [ --dimlevel level --dim device ]
                      [ --up device --down device ]

       --list (-l short option)
             List currently configured devices and sensors.

       --sensor sensor (-s short option)
             Display information from the specified sensor.

       --on device (-n short option)
             Turns on device. 'device' must be an integer of the device-id
             Device-id and name is outputed with the --list option

       --off device (-f short option)
             Turns off device. 'device' must be an integer of the device-id
             Device-id and name is outputed with the --list option

       --dim device (-d short option)
             Dims device. 'device' must be an integer of the device-id
             Device-id and name is outputed with the --list option
             Note: The dimlevel parameter must be set before using this option.

       --dimlevel level (-v short option)
             Set dim level. 'level' should an integer, 0-255.
             Note: This parameter must be set before using dim.

       --bell device (-b short option)
             Sends bell command to devices supporting this. 'device' must
             be an integer of the device-id
             Device-id and name is outputed with the --list option

       --up device
             Sends up command to devices supporting this. 'device' must
             be an integer of the device-id
             Device-id and name is outputed with the --list option

       --down device
             Sends down command to devices supporting this. 'device' must
             be an integer of the device-id
             Device-id and name is outputed with the --list option

       --help (-h short option)
             Shows this screen.

Report bugs to <klippo@deny.se>
