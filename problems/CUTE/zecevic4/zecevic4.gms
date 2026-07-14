* GAMS-model zecevic4.dag.gms written by dag2gams Converter at 29/03/2004 16:53:53
* University of Vienna
$offdigit;
 Set i/1*2/;
 Set j/1*2/;
 Equations objcon
con1
con2
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= (-60) * x('1') - 
8 * x('2') + 
power(x('2'), 2) + 
6 * power(x('1'), 2) + 166;


con1..-x('1') - 
x('2') =l= -3;
con2..-x('1') - 
x('2') + 
x('1') * x('2') =l= 0;
x.lo('1')=-0;
x.up('1')=10;
x.lo('2')=-0;
x.up('2')=10;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


