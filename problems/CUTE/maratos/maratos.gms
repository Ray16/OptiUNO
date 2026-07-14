* GAMS-model maratos.dag.gms written by dag2gams Converter at 29/03/2004 16:53:53
* University of Vienna
$offdigit;
 Set i/1*1/;
 Set j/1*2/;
 Equations objcon
con1
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= -x('1') + 
9.9999999999999995e-07 * power(x('1'), 2) + 
9.9999999999999995e-07 * power(x('2'), 2) - 9.9999999999999995e-07;


con1.. power(x('1'), 2) + 
power(x('2'), 2) =e= 1;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


