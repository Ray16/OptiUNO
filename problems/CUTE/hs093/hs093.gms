* GAMS-model hs093.dag.gms written by dag2gams Converter at 29/03/2004 17:00:0
* University of Vienna
$offdigit;
 Set i/1*2/;
 Set j/1*6/;
 Equations objcon
con1
con2
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= 0.020400000000000001 * x('1') * x('4') * (x('1') + 
x('2') + 
x('3')) + 
0.018700000000000001 * x('2') * x('3') * (x('1') + 
1.5700000000000001 * x('2') + 
x('4')) + 
0.060699999999999997 * x('1') * x('4') * (x('1') + 
x('2') + 
x('3')) * power(x('5'), 2) + 
0.043700000000000003 * x('2') * x('3') * (x('1') + 
1.5700000000000001 * x('2') + 
x('4')) * power(x('6'), 2);


con1..0.00062 * x('1') * x('4') * (x('1') + 
x('2') + 
x('3')) * power(x('5'), 2) + 
0.00058 * x('2') * x('3') * (x('1') + 
1.5700000000000001 * x('2') + 
x('4')) * power(x('6'), 2) =l= 1;
con2..x('1') * x('2') * x('3') * x('4') * x('5') * x('6') =g= 2069.9999999999995;
x.lo('1')=0;
x.lo('2')=0;
x.lo('3')=0;
x.lo('4')=0;
x.lo('5')=0;
x.lo('6')=0;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


