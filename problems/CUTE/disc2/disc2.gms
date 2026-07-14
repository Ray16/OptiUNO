* GAMS-model disc2.dag.gms written by dag2gams Converter at 29/03/2004 16:59:59
* University of Vienna
$offdigit;
 Set i/1*23/;
 Set j/1*28/;
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
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= x('1');


con1.. -x('11') + 
x('23') - 
x('28') * (x('3') - 
x('11')) =e= 0;
con2.. -x('10') + 
x('22') - 
x('28') * (x('2') - 
x('10')) =e= 0;
con3.. -power(x('1'), 2) + 
power(x('2'), 2) + 
power((x('3')) - 10, 2) =e= 0;
con4.. -x('11') + 
x('21') - 
x('28') * (x('3') - 
x('11')) =e= 0;
con5.. -power(x('1'), 2) + 
power((x('4')) - 8, 2) + 
power((x('5')) - 10, 2) =e= 0;
con6.. -x('10') + 
x('20') - 
x('28') * (x('2') - 
x('10')) =e= 0;
con7.. -x('9') + 
x('19') - 
x('27') * ((- x('9')) + 
x('11')) =e= 0;
con8.. -power(x('1'), 2) + 
power((x('6')) - 12, 2) + 
power((x('7')) - 5, 2) =e= 0;
con9.. -x('8') + 
x('18') - 
x('27') * ((- x('8')) + 
x('10')) =e= 0;
con10.. -x('7') + 
x('17') - 
x('26') * ((- x('7')) + 
x('9')) =e= 0;
con11.. -power(x('1'), 2) + 
power(x('9'), 2) + 
power((x('8')) - 8, 2) =e= 0;
con12.. -x('6') + 
x('16') - 
x('26') * ((- x('6')) + 
x('8')) =e= 0;
con13.. -power(x('1'), 2) + 
power(x('10'), 2) + 
power(x('11'), 2) =e= 0;
con14.. -x('5') + 
x('15') - 
x('25') * ((- x('5')) + 
x('7')) =e= 0;
con15.. -x('4') + 
x('14') - 
x('25') * ((- x('4')) + 
x('6')) =e= 0;
con16.. -x('3') + 
x('13') - 
x('24') * ((- x('3')) + 
x('5')) =e= 0;
con17.. -x('2') + 
x('12') - 
x('24') * ((- x('2')) + 
x('4')) =e= 0;
con18..power(x('1'), 2) - 
power((x('12')) - 4, 2) - 
power((x('13')) - 8, 2) =g= 0;
con19..power(x('1'), 2) - 
power((x('14')) - 8, 2) - 
power((x('15')) - 7, 2) =g= 0;
con20..power(x('1'), 2) - 
power((x('16')) - 8, 2) - 
power((x('17')) - 3, 2) =g= 0;
con21..power(x('1'), 2) - 
power((x('22')) - 2, 2) - 
power((x('23')) - 6, 2) =g= 0;
con22..power(x('1'), 2) - 
power((x('18')) - 4, 2) - 
power((x('19')) - 1, 2) =g= 0;
con23..power(x('1'), 2) - 
power((x('20')) - 2, 2) - 
power((x('21')) - 3, 2) =g= 0;
x.lo('1')=0;
x.up('1')=3;
x.lo('24')=0;
x.up('24')=1;
x.lo('25')=0;
x.up('25')=1;
x.lo('26')=0;
x.up('26')=1;
x.lo('27')=0;
x.up('27')=1;
x.lo('28')=0;
x.up('28')=1;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


