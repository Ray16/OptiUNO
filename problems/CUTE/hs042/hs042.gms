* GAMS-model hs042.dag.gms written by dag2gams Converter at 29/03/2004 16:59:08
* University of Vienna
$offdigit;
 Set i/1*1/;
 Set j/1*4/;
 Equations objcon
con1
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= power((x('1')) - 3, 2) + 
power((x('2')) - 4, 2) + 
power((x('3')) - 1, 2) + 
power((x('4')) - 2, 2);


con1.. power(x('1'), 2) + 
power(x('2'), 2) =e= 2;
x.lo('3')=2;
x.up('3')=2;
x.lo('1')=0;
x.lo('2')=0;
x.lo('4')=0;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


