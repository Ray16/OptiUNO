* GAMS-model discs.dag.gms written by dag2gams Converter at 29/03/2004 16:59:59
* University of Vienna
$offdigit;
 Set i/1*66/;
 Set j/1*36/;
 Equations objcon
con1
con2
con3
con4
con5
con6
con7
con8
con9
con10
con11
con12
con13
con14
con15
con16
con17
con18
con19
con20
con21
con22
con23
con24
con25
con26
con27
con28
con29
con30
con31
con32
con33
con34
con35
con36
con37
con38
con39
con40
con41
con42
con43
con44
con45
con46
con47
con48
con49
con50
con51
con52
con53
con54
con55
con56
con57
con58
con59
con60
con61
con62
con63
con64
con65
con66
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= x('25') + 
x('26') + 
x('27') + 
x('28') + 
x('29') + 
x('30') + 
x('31') + 
x('32') + 
x('33') + 
x('34') + 
x('35') + 
x('36');


con1.. -power(-x('1') + 
x('2'), 2) - 
power(-x('13') + 
x('14'), 2) + 
power(x('25') + 
x('26'), 2) =e= 0;
con2.. -power(-x('2') + 
x('3'), 2) - 
power(-x('14') + 
x('15'), 2) + 
power(x('26') + 
x('27'), 2) =e= 0;
con3.. -power(-x('2') + 
x('4'), 2) - 
power(-x('14') + 
x('16'), 2) + 
power(x('26') + 
x('28'), 2) =e= 0;
con4.. -power(-x('3') + 
x('4'), 2) - 
power(-x('15') + 
x('16'), 2) + 
power(x('27') + 
x('28'), 2) =e= 0;
con5.. -power(-x('4') + 
x('5'), 2) - 
power(-x('16') + 
x('17'), 2) + 
power(x('28') + 
x('29'), 2) =e= 0;
con6.. -power(-x('4') + 
x('6'), 2) - 
power(-x('16') + 
x('18'), 2) + 
power(x('28') + 
x('30'), 2) =e= 0;
con7.. -power(-x('5') + 
x('6'), 2) - 
power(-x('17') + 
x('18'), 2) + 
power(x('29') + 
x('30'), 2) =e= 0;
con8.. -power(-x('1') + 
x('7'), 2) - 
power(-x('13') + 
x('19'), 2) + 
power(x('25') + 
x('31'), 2) =e= 0;
con9.. -power(-x('6') + 
x('7'), 2) - 
power(-x('18') + 
x('19'), 2) + 
power(x('30') + 
x('31'), 2) =e= 0;
con10.. -power(-x('7') + 
x('8'), 2) - 
power(-x('19') + 
x('20'), 2) + 
power(x('31') + 
x('32'), 2) =e= 0;
con11.. -power(-x('7') + 
x('9'), 2) - 
power(-x('19') + 
x('21'), 2) + 
power(x('31') + 
x('33'), 2) =e= 0;
con12.. -power(-x('8') + 
x('9'), 2) - 
power(-x('20') + 
x('21'), 2) + 
power(x('32') + 
x('33'), 2) =e= 0;
con13.. -power(-x('8') + 
x('10'), 2) - 
power(-x('20') + 
x('22'), 2) + 
power(x('32') + 
x('34'), 2) =e= 0;
con14.. -power(-x('9') + 
x('10'), 2) - 
power(-x('21') + 
x('22'), 2) + 
power(x('33') + 
x('34'), 2) =e= 0;
con15.. -power(-x('5') + 
x('11'), 2) - 
power(-x('17') + 
x('23'), 2) + 
power(x('29') + 
x('35'), 2) =e= 0;
con16.. -power(-x('10') + 
x('11'), 2) - 
power(-x('22') + 
x('23'), 2) + 
power(x('34') + 
x('35'), 2) =e= 0;
con17.. -power(-x('10') + 
x('12'), 2) - 
power(-x('22') + 
x('24'), 2) + 
power(x('34') + 
x('36'), 2) =e= 0;
con18.. -power(-x('11') + 
x('12'), 2) - 
power(-x('23') + 
x('24'), 2) + 
power(x('35') + 
x('36'), 2) =e= 0;
con19..-power(-x('9') + 
x('12'), 2) - 
power(-x('21') + 
x('24'), 2) + 
power(x('33') + 
x('36'), 2) =l= -0.0001;
con20..-power(-x('8') + 
x('12'), 2) - 
power(-x('20') + 
x('24'), 2) + 
power(x('32') + 
x('36'), 2) =l= -0.0001;
con21..-power(-x('7') + 
x('12'), 2) - 
power(-x('19') + 
x('24'), 2) + 
power(x('31') + 
x('36'), 2) =l= -0.0001;
con22..-power(-x('6') + 
x('12'), 2) - 
power(-x('18') + 
x('24'), 2) + 
power(x('30') + 
x('36'), 2) =l= -0.0001;
con23..-power(-x('5') + 
x('12'), 2) - 
power(-x('17') + 
x('24'), 2) + 
power(x('29') + 
x('36'), 2) =l= -0.0001;
con24..-power(-x('4') + 
x('12'), 2) - 
power(-x('16') + 
x('24'), 2) + 
power(x('28') + 
x('36'), 2) =l= -0.0001;
con25..-power(-x('3') + 
x('12'), 2) - 
power(-x('15') + 
x('24'), 2) + 
power(x('27') + 
x('36'), 2) =l= -0.0001;
con26..-power(-x('2') + 
x('12'), 2) - 
power(-x('14') + 
x('24'), 2) + 
power(x('26') + 
x('36'), 2) =l= -0.0001;
con27..-power(-x('1') + 
x('12'), 2) - 
power(-x('13') + 
x('24'), 2) + 
power(x('25') + 
x('36'), 2) =l= -0.0001;
con28..-power(-x('9') + 
x('11'), 2) - 
power(-x('21') + 
x('23'), 2) + 
power(x('33') + 
x('35'), 2) =l= -0.0001;
con29..-power(-x('8') + 
x('11'), 2) - 
power(-x('20') + 
x('23'), 2) + 
power(x('32') + 
x('35'), 2) =l= -0.0001;
con30..-power(-x('7') + 
x('11'), 2) - 
power(-x('19') + 
x('23'), 2) + 
power(x('31') + 
x('35'), 2) =l= -0.0001;
con31..-power(-x('6') + 
x('11'), 2) - 
power(-x('18') + 
x('23'), 2) + 
power(x('30') + 
x('35'), 2) =l= -0.0001;
con32..-power(-x('1') + 
x('3'), 2) - 
power(-x('13') + 
x('15'), 2) + 
power(x('25') + 
x('27'), 2) =l= -0.0001;
con33..-power(-x('4') + 
x('11'), 2) - 
power(-x('16') + 
x('23'), 2) + 
power(x('28') + 
x('35'), 2) =l= -0.0001;
con34..-power(-x('1') + 
x('4'), 2) - 
power(-x('13') + 
x('16'), 2) + 
power(x('25') + 
x('28'), 2) =l= -0.0001;
con35..-power(-x('3') + 
x('11'), 2) - 
power(-x('15') + 
x('23'), 2) + 
power(x('27') + 
x('35'), 2) =l= -0.0001;
con36..-power(-x('1') + 
x('5'), 2) - 
power(-x('13') + 
x('17'), 2) + 
power(x('25') + 
x('29'), 2) =l= -0.0001;
con37..-power(-x('2') + 
x('11'), 2) - 
power(-x('14') + 
x('23'), 2) + 
power(x('26') + 
x('35'), 2) =l= -0.0001;
con38..-power(-x('2') + 
x('5'), 2) - 
power(-x('14') + 
x('17'), 2) + 
power(x('26') + 
x('29'), 2) =l= -0.0001;
con39..-power(-x('1') + 
x('11'), 2) - 
power(-x('13') + 
x('23'), 2) + 
power(x('25') + 
x('35'), 2) =l= -0.0001;
con40..-power(-x('3') + 
x('5'), 2) - 
power(-x('15') + 
x('17'), 2) + 
power(x('27') + 
x('29'), 2) =l= -0.0001;
con41..-power(-x('7') + 
x('10'), 2) - 
power(-x('19') + 
x('22'), 2) + 
power(x('31') + 
x('34'), 2) =l= -0.0001;
con42..-power(-x('1') + 
x('6'), 2) - 
power(-x('13') + 
x('18'), 2) + 
power(x('25') + 
x('30'), 2) =l= -0.0001;
con43..-power(-x('2') + 
x('6'), 2) - 
power(-x('14') + 
x('18'), 2) + 
power(x('26') + 
x('30'), 2) =l= -0.0001;
con44..-power(-x('6') + 
x('10'), 2) - 
power(-x('18') + 
x('22'), 2) + 
power(x('30') + 
x('34'), 2) =l= -0.0001;
con45..-power(-x('3') + 
x('6'), 2) - 
power(-x('15') + 
x('18'), 2) + 
power(x('27') + 
x('30'), 2) =l= -0.0001;
con46..-power(-x('5') + 
x('10'), 2) - 
power(-x('17') + 
x('22'), 2) + 
power(x('29') + 
x('34'), 2) =l= -0.0001;
con47..-power(-x('2') + 
x('7'), 2) - 
power(-x('14') + 
x('19'), 2) + 
power(x('26') + 
x('31'), 2) =l= -0.0001;
con48..-power(-x('4') + 
x('10'), 2) - 
power(-x('16') + 
x('22'), 2) + 
power(x('28') + 
x('34'), 2) =l= -0.0001;
con49..-power(-x('3') + 
x('7'), 2) - 
power(-x('15') + 
x('19'), 2) + 
power(x('27') + 
x('31'), 2) =l= -0.0001;
con50..-power(-x('3') + 
x('10'), 2) - 
power(-x('15') + 
x('22'), 2) + 
power(x('27') + 
x('34'), 2) =l= -0.0001;
con51..-power(-x('4') + 
x('7'), 2) - 
power(-x('16') + 
x('19'), 2) + 
power(x('28') + 
x('31'), 2) =l= -0.0001;
con52..-power(-x('2') + 
x('10'), 2) - 
power(-x('14') + 
x('22'), 2) + 
power(x('26') + 
x('34'), 2) =l= -0.0001;
con53..-power(-x('5') + 
x('7'), 2) - 
power(-x('17') + 
x('19'), 2) + 
power(x('29') + 
x('31'), 2) =l= -0.0001;
con54..-power(-x('1') + 
x('10'), 2) - 
power(-x('13') + 
x('22'), 2) + 
power(x('25') + 
x('34'), 2) =l= -0.0001;
con55..-power(-x('1') + 
x('8'), 2) - 
power(-x('13') + 
x('20'), 2) + 
power(x('25') + 
x('32'), 2) =l= -0.0001;
con56..-power(-x('2') + 
x('8'), 2) - 
power(-x('14') + 
x('20'), 2) + 
power(x('26') + 
x('32'), 2) =l= -0.0001;
con57..-power(-x('6') + 
x('9'), 2) - 
power(-x('18') + 
x('21'), 2) + 
power(x('30') + 
x('33'), 2) =l= -0.0001;
con58..-power(-x('3') + 
x('8'), 2) - 
power(-x('15') + 
x('20'), 2) + 
power(x('27') + 
x('32'), 2) =l= -0.0001;
con59..-power(-x('5') + 
x('9'), 2) - 
power(-x('17') + 
x('21'), 2) + 
power(x('29') + 
x('33'), 2) =l= -0.0001;
con60..-power(-x('4') + 
x('8'), 2) - 
power(-x('16') + 
x('20'), 2) + 
power(x('28') + 
x('32'), 2) =l= -0.0001;
con61..-power(-x('4') + 
x('9'), 2) - 
power(-x('16') + 
x('21'), 2) + 
power(x('28') + 
x('33'), 2) =l= -0.0001;
con62..-power(-x('5') + 
x('8'), 2) - 
power(-x('17') + 
x('20'), 2) + 
power(x('29') + 
x('32'), 2) =l= -0.0001;
con63..-power(-x('3') + 
x('9'), 2) - 
power(-x('15') + 
x('21'), 2) + 
power(x('27') + 
x('33'), 2) =l= -0.0001;
con64..-power(-x('6') + 
x('8'), 2) - 
power(-x('18') + 
x('20'), 2) + 
power(x('30') + 
x('32'), 2) =l= -0.0001;
con65..-power(-x('2') + 
x('9'), 2) - 
power(-x('14') + 
x('21'), 2) + 
power(x('26') + 
x('33'), 2) =l= -0.0001;
con66..-power(-x('1') + 
x('9'), 2) - 
power(-x('13') + 
x('21'), 2) + 
power(x('25') + 
x('33'), 2) =l= -0.0001;
x.lo('1')=-0;
x.up('1')=0;
x.lo('13')=-0;
x.up('13')=0;
x.lo('14')=-0;
x.up('14')=0;
x.lo('25')=1;
x.lo('26')=1;
x.lo('27')=1;
x.lo('28')=1;
x.lo('29')=1;
x.lo('30')=1;
x.lo('31')=1;
x.lo('32')=1;
x.lo('33')=1;
x.lo('34')=1;
x.lo('35')=1;
x.lo('36')=1;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


