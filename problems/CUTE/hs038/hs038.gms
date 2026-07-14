* GAMS-model hs038.dag.gms written by dag2gams Converter at 29/03/2004 16:59:07
* University of Vienna
$offdigit;
 Set j/1*4/;
 Equations objcon
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= power(((- x('1'))) + 1, 2) + 
power(((- x('3'))) + 1, 2) + 
10.1 * power((x('2')) - 1, 2) + 
10.1 * power((x('4')) - 1, 2) + 
(19.800000000000001 * x('2') - 
19.800000000000001) * (x('4') - 
1) + 
100 * power(x('2') - 
power(x('1'), 2), 2) + 
90 * power(x('4') - 
power(x('3'), 2), 2);


x.lo('1')=-10;
x.up('1')=10;
x.lo('2')=-10;
x.up('2')=10;
x.lo('3')=-10;
x.up('3')=10;
x.lo('4')=-10;
x.up('4')=10;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


