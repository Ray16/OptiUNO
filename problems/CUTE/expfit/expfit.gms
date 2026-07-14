* GAMS-model expfit.dag.gms written by dag2gams Converter at 29/03/2004 16:53:53
* University of Vienna
$offdigit;
 Set j/1*2/;
 Equations objcon
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= power((exp(0.25 * x('2')) * x('1')) - 0.25, 2) + 
power((exp(0.5 * x('2')) * x('1')) - 0.5, 2) + 
power((exp(0.75 * x('2')) * x('1')) - 0.75, 2) + 
power((exp(x('2')) * x('1')) - 1, 2) + 
power((exp(1.25 * x('2')) * x('1')) - 1.25, 2) + 
power((exp(1.5 * x('2')) * x('1')) - 1.5, 2) + 
power((exp(1.75 * x('2')) * x('1')) - 1.75, 2) + 
power((exp(2 * x('2')) * x('1')) - 2, 2) + 
power((exp(2.25 * x('2')) * x('1')) - 2.25, 2) + 
power((exp(2.5 * x('2')) * x('1')) - 2.5, 2);


Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


