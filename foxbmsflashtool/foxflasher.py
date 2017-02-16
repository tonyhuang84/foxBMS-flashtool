"""
foxBMS Software License

Copyright 2010-2016, Fraunhofer-Gesellschaft zur Foerderung 
                     der angewandten Forschung e.V.
All rights reserved.

BSD 3-Clause License

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

  1.  Redistributions of source code must retain the above copyright notice,
      this list of conditions and the following disclaimer.
  2.  Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
  3.  Neither the name of the copyright holder nor the names of its
      contributors may be used to endorse or promote products derived from
      this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.

We kindly request you to use one or more of the following phrases to refer
to foxBMS in your hardware, software, documentation or advertising
materials:

"This product uses parts of foxBMS"
"This product includes parts of foxBMS"
"This product is derived from foxBMS"

If you use foxBMS in your products, we encourage you to contact us at:

CONTACT INFORMATION
Fraunhofer IISB ; Schottkystrasse 10 ; 91058 Erlangen, Germany
Dr.-Ing. Vincent LORENTZ
+49 9131-761-346
info@foxbms.org
www.foxbms.org

:author:    Martin Giegerich <martin.giegerich@iisb.fraunhofer.de>
"""

import stm32flasher
import argparse, sys 
import time
import logging

class FoxFlasher(stm32flasher.STM32Flasher):
    def __init__(self, port=None, file=None, **kwargs):
        stm32flasher.STM32Flasher.__init__(self, port, file, **kwargs)
        
    def _doBeforeInit(self):
        self.enterBootmode()
        self.reset()
        
    def reset(self):
        ''' resets the microcontroller by giving a pulse to RESET pin '''
        self._port.setRTS(1)
        time.sleep(0.5)
        self._port.setRTS(0)
        time.sleep(0.5)

    def enterBootmode(self):
        ''' sets DTR pin, which is connected to microcontroller BOOT pin '''
        self._port.setDTR(1)
        
def auto_int(x):
    return int(x, 0)

def main():
    parser = argparse.ArgumentParser(description='foxBMS---STM32 flash tool', 
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog = '''\
Example:
%s --port COM3 --erase --write --verify build/src/general/foxbms_flash.bin 

Copyright (c) 2015, 2016 Fraunhofer IISB.
All rights reserved.
This program has been released under the conditions of the 3-clause BSD
license.
''' % sys.argv[0])
    
    parser.add_argument('-v', '--verbosity', action='count', default=0, help="increase output verbosity")
    parser.add_argument('--erase', '-e', action='store_true', help='erase firmware')
    parser.add_argument('--read',  '-r', action='store_true', help='read and store firmware')
    parser.add_argument('--write',  '-w', action='store_true', help='writes firmware')
    parser.add_argument('--verify', '-y', action='store_true', help='verify the firmware')
    parser.add_argument('--bytes', '-s', type=int, help='bytes to read from the firmware')
    parser.add_argument('--bauds', '-b', type=int, default=115200, help='transfer speed (bauds)')
    parser.add_argument('--port', '-p', type=str, default='/dev/tty.usbserial-ftCYPMYJ', help='ttyUSB port')
    parser.add_argument('--address', '-a', type=auto_int, default=0x08000000, help='target address')
    parser.add_argument('--goaddress', '-g', type=auto_int, default=-1, help='start address (use -1 for default)')
    parser.add_argument('firmware', metavar = 'FIRMWARE FILE', help='firmware binary')
    
    args = parser.parse_args()
    
    if args.verbosity == 1:
        logging.basicConfig(level = logging.INFO)
    elif args.verbosity > 1:
        logging.basicConfig(level = logging.DEBUG)
    else:
        logging.basicConfig(level = logging.ERROR)

    if args.read:
        if args.erase:
            parser.error('Cannot use --erase together with --read')
        if args.write:
            parser.error('Cannot use --write together with --read')
        if args.bytes == None:
            parser.error('Please give a length (in bytes) to read')
            
    with FoxFlasher(**vars(args)) as ff:
#         ff.enterBootmode()
#         ff.reset()
#         ff.init()
        if args.write or args.verify:
            with open(args.firmware, 'rb') as f:
                data = map(lambda c: ord(c), f.read())

        if args.erase:
            ff.erase()

        if args.write:
            ff.write(data)

        if args.verify:
            ff.verify(data)

        if args.read:
            rdata = ff.read()
            with open(args.firmware, 'wb') as f:
                f.write(''.join(map(chr,rdata)))

        if args.goaddress > -1:
            ff.go(args.goaddress)
            
if __name__ == "__main__":
    main()