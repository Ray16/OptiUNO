* GAMS-model lotschd.dag.gms written by dag2gams Converter at 29/03/2004 16:59:05
* University of Vienna
$offdigit;
 Set i/1*7/;
 Set j/1*12/;
 Equations objcon
con1
con2
con3
con4
con5
con6
con7
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= power(1.502 * x('1'), 2) + 
power(1.1259999999999999 * x('2'), 2) + 
power(0.81499999999999995 * x('3'), 2) + 
power(1.268 * x('4'), 2) + 
power(1.502 * x('5'), 2) + 
power(0.73999999999999999 * x('6'), 2);


con1.. x('1') + 
x('2') + 
x('3') + 
x('4') + 
x('5') + 
x('6') + 
x('7') + 
x('8') + 
x('9') + 
x('10') + 
x('11') + 
x('12') =e= 126.09999999999999;
con2.. -x('1') - 
x('2') - 
x('3') - 
x('4') - 
x('5') + 
7.4000000000000004 * x('6') - 
x('7') - 
x('8') - 
x('9') - 
x('10') - 
x('11') - 
x('12') =e= 20;
con3.. -x('1') + 
1.8 * x('5') - 
x('7') - 
x('11') =e= 9;
con4.. -x('1') + 
2.2000000000000002 * x('4') - 
x('5') - 
x('6') - 
x('7') - 
2 * x('10') - 
x('11') - 
x('12') =e= 17;
con5.. -x('1') - 
x('2') + 
5.0999999999999996 * x('3') - 
x('4') - 
x('5') - 
x('6') - 
x('7') - 
x('8') - 
2 * x('9') - 
x('10') - 
x('11') - 
x('12') =e= 20;
con6.. 2.2000000000000002 * x('2') - 
x('3') - 
2 * x('8') - 
x('9') =e= 3;
con7.. 1.8 * x('1') - 
x('7') =e= 11;
x.lo('1')=0;
x.lo('2')=0;
x.lo('3')=0;
x.lo('4')=0;
x.lo('5')=0;
x.lo('6')=0;
x.lo('7')=0;
x.lo('8')=0;
x.lo('9')=0;
x.lo('10')=0;
x.lo('11')=0;
x.lo('12')=0;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


