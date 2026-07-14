* GAMS-model humps.dag.gms written by dag2gams Converter at 29/03/2004 16:53:53
* University of Vienna
$offdigit;
 Set j/1*2/;
 Equations objcon
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= power(sin(20 * x('1')) * sin(20 * x('2')), 2) + 
0.050000000000000003 * power(x('1'), 2) + 
0.050000000000000003 * power(x('2'), 2);


Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


