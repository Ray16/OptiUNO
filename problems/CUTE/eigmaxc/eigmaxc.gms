* GAMS-model eigmaxc.dag.gms written by dag2gams Converter at 29/03/2004 16:59:59
* University of Vienna
$offdigit;
 Set i/1*22/;
 Set j/1*22/;
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
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= -(x('1'));


con1.. power(x('2'), 2) + 
power(x('3'), 2) + 
power(x('4'), 2) + 
power(x('5'), 2) + 
power(x('6'), 2) + 
power(x('7'), 2) + 
power(x('8'), 2) + 
power(x('9'), 2) + 
power(x('10'), 2) + 
power(x('11'), 2) + 
power(x('12'), 2) + 
power(x('13'), 2) + 
power(x('14'), 2) + 
power(x('15'), 2) + 
power(x('16'), 2) + 
power(x('17'), 2) + 
power(x('18'), 2) + 
power(x('19'), 2) + 
power(x('20'), 2) + 
power(x('21'), 2) + 
power(x('22'), 2) =e= 1;
con2.. -x('21') + 
10 * x('22') + 
x('1') * x('22') =e= 0;
con3.. -x('20') + 
9 * x('21') - 
x('22') + 
x('1') * x('21') =e= 0;
con4.. -x('19') + 
8 * x('20') - 
x('21') + 
x('1') * x('20') =e= 0;
con5.. -x('18') + 
7 * x('19') - 
x('20') + 
x('1') * x('19') =e= 0;
con6.. -x('17') + 
6 * x('18') - 
x('19') + 
x('1') * x('18') =e= 0;
con7.. -x('16') + 
5 * x('17') - 
x('18') + 
x('1') * x('17') =e= 0;
con8.. -x('15') + 
4 * x('16') - 
x('17') + 
x('1') * x('16') =e= 0;
con9.. -x('14') + 
3 * x('15') - 
x('16') + 
x('1') * x('15') =e= 0;
con10.. -x('13') + 
2 * x('14') - 
x('15') + 
x('1') * x('14') =e= 0;
con11.. -x('12') + 
x('13') - 
x('14') + 
x('1') * x('13') =e= 0;
con12.. -x('11') - 
x('13') + 
x('1') * x('12') =e= 0;
con13.. (-10) * x('2') - 
x('3') + 
x('1') * x('2') =e= 0;
con14.. -x('10') - 
x('11') - 
x('12') + 
x('1') * x('11') =e= 0;
con15.. -x('9') - 
2 * x('10') - 
x('11') + 
x('1') * x('10') =e= 0;
con16.. -x('2') - 
9 * x('3') - 
x('4') + 
x('1') * x('3') =e= 0;
con17.. -x('8') - 
3 * x('9') - 
x('10') + 
x('1') * x('9') =e= 0;
con18.. -x('7') - 
4 * x('8') - 
x('9') + 
x('1') * x('8') =e= 0;
con19.. -x('3') - 
8 * x('4') - 
x('5') + 
x('1') * x('4') =e= 0;
con20.. -x('6') - 
5 * x('7') - 
x('8') + 
x('1') * x('7') =e= 0;
con21.. -x('5') - 
6 * x('6') - 
x('7') + 
x('1') * x('6') =e= 0;
con22.. -x('4') - 
7 * x('5') - 
x('6') + 
x('1') * x('5') =e= 0;
x.lo('2')=-1;
x.up('2')=1;
x.lo('3')=-1;
x.up('3')=1;
x.lo('4')=-1;
x.up('4')=1;
x.lo('5')=-1;
x.up('5')=1;
x.lo('6')=-1;
x.up('6')=1;
x.lo('7')=-1;
x.up('7')=1;
x.lo('8')=-1;
x.up('8')=1;
x.lo('9')=-1;
x.up('9')=1;
x.lo('10')=-1;
x.up('10')=1;
x.lo('11')=-1;
x.up('11')=1;
x.lo('12')=-1;
x.up('12')=1;
x.lo('13')=-1;
x.up('13')=1;
x.lo('14')=-1;
x.up('14')=1;
x.lo('15')=-1;
x.up('15')=1;
x.lo('16')=-1;
x.up('16')=1;
x.lo('17')=-1;
x.up('17')=1;
x.lo('18')=-1;
x.up('18')=1;
x.lo('19')=-1;
x.up('19')=1;
x.lo('20')=-1;
x.up('20')=1;
x.lo('21')=-1;
x.up('21')=1;
x.lo('22')=-1;
x.up('22')=1;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


