* GAMS-model hs035.dag.gms written by dag2gams Converter at 29/03/2004 16:58:58
* University of Vienna
$offdigit;
 Set i/1*1/;
 Set j/1*3/;
 Equations objcon
con1
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= (-8) * x('1') - 
6 * x('2') - 
4 * x('3') + 
power(x('3'), 2) + 
2 * power(x('1'), 2) + 
2 * power(x('2'), 2) + 
2 * x('1') * x('2') + 
2 * x('1') * x('3') + 9;


con1..x('1') + 
x('2') + 
2 * x('3') =l= 3;
x.lo('1')=0;
x.lo('2')=0;
x.lo('3')=0;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


