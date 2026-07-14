* GAMS-model cb3.dag.gms written by dag2gams Converter at 29/03/2004 16:58:58
* University of Vienna
$offdigit;
 Set i/1*3/;
 Set j/1*3/;
 Equations objcon
con1
con2
con3
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= x('3');


con1..x('3') - 
power(x('2'), 2) - 
power(x('1'), 4) =g= 0;
con2..(-2) * exp(-x('1') + 
x('2')) + 
x('3') =g= 0;
con3..x('3') - 
power(((- x('1'))) + 2, 2) - 
power(((- x('2'))) + 2, 2) =g= 0;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


