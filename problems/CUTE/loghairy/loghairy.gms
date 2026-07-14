* GAMS-model loghairy.dag.gms written by dag2gams Converter at 29/03/2004 16:53:53
* University of Vienna
$offdigit;
 Set j/1*2/;
 Equations objcon
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= log(0.01 * (100 * sqrt(power(x('1'), 2) + 0.01) + 
100 * sqrt(power(x('1') - 
x('2'), 2) + 0.01) + 
30 * power(sin(7 * x('1')), 2) * power(cos(7 * x('2')), 2) + 
100));


Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


