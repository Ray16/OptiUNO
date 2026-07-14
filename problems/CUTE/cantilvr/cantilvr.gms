* GAMS-model cantilvr.dag.gms written by dag2gams Converter at 29/03/2004 17:00:0
* University of Vienna
$offdigit;
 Set i/1*1/;
 Set j/1*5/;
 Equations objcon
con1
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= 0.062399999999999997 * x('1') + 
0.062399999999999997 * x('2') + 
0.062399999999999997 * x('3') + 
0.062399999999999997 * x('4') + 
0.062399999999999997 * x('5');


con1..61 * (1/power(x('1'), 3)) + 
37 * (1/power(x('2'), 3)) + 
19 * (1/power(x('3'), 3)) + 
7 * (1/power(x('4'), 3)) + 
1/power(x('5'), 3) =l= 1;
x.lo('1')=9.9999999999999995e-07;
x.lo('2')=9.9999999999999995e-07;
x.lo('3')=9.9999999999999995e-07;
x.lo('4')=9.9999999999999995e-07;
x.lo('5')=9.9999999999999995e-07;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


