* GAMS-model hatflda.dag.gms written by dag2gams Converter at 29/03/2004 16:59:07
* University of Vienna
$offdigit;
 Set j/1*4/;
 Equations objcon
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= power(-sqrt(x('2')) + 
x('1'), 2) + 
power(-sqrt(x('3')) + 
x('2'), 2) + 
power(-sqrt(x('4')) + 
x('3'), 2) + 
power((x('1')) - 1, 2);


x.lo('1')=9.9999999999999995e-08;
x.lo('2')=9.9999999999999995e-08;
x.lo('3')=9.9999999999999995e-08;
x.lo('4')=9.9999999999999995e-08;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


