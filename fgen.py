#!/usr/bin/env python
from instruments.gpib import prologix
from instruments.fgen import HP8116A
def main():
    plx = prologix(port = 1)
    inst = HP8116A(plx, 16, delay = 0.05, auto = False)
    inst.write('++read_tmo_ms 3000')
    inst.write('++eos 2')
    inst.write('++eot_enable 1')
    inst.frequency = 200000
    #print zip(f, t, m)
    #inst.chart_type = ChartTypes.LOG_MAG

if __name__ == "__main__":
    main()