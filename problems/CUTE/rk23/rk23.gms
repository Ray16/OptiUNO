* GAMS-model rk23.dag.gms written by dag2gams Converter at 29/03/2004 16:59:06
* University of Vienna
$offdigit;
 Set i/1*11/;
 Set j/1*17/;
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
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= x('12') + 
x('13') + 
x('14') + 
x('15') + 
x('16') + 
x('17');


con1.. x('6') + 
x('7') + 
x('11') =e= 1;
con2.. x('4') + 
x('5') + 
x('10') =e= 1;
con3.. -x('2') + 
x('3') + 
x('9') =e= 0;
con4.. -x('1') + 
x('8') =e= 0;
con5.. x('1') * x('4') + 
x('2') * x('5') =e= 0.5;
con6.. x('1') * x('6') + 
x('2') * x('7') =e= 0.5;
con7.. x('6') * power(x('1'), 2) + 
x('7') * power(x('2'), 2) =e= 0.33333333333333331;
con8.. x('16') - 
x('17') + 
12 * x('3') * x('7') * power(x('1'), 2) =e= 1;
con9.. x('14') - 
x('15') + 
8 * x('1') * x('2') * x('3') * x('7') =e= 1;
con10.. x('1') * x('3') * x('7') =e= 0.16666666666666666;
con11.. x('12') - 
x('15') + 
4 * x('6') * power(x('1'), 3) + 
4 * x('7') * power(x('2'), 3) =e= 1;
x.lo('12')=0;
x.lo('13')=0;
x.lo('14')=0;
x.lo('15')=0;
x.lo('16')=0;
x.lo('17')=0;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


