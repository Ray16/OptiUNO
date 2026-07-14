* GAMS-model bt13.dag.gms written by dag2gams Converter at 29/03/2004 17:00:0
* University of Vienna
$offdigit;
 Set i/1*1/;
 Set j/1*5/;
 Equations objcon
con1
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= x('5');


con1.. power(x('1'), 2) - 
power(x('5'), 2) + 
power(x('1') - 
2 * x('2'), 2) + 
power(x('2') - 
3 * x('3'), 2) + 
power(x('3') - 
4 * x('4'), 2) =e= 0;
x.lo('5')=-0;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


