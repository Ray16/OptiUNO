* GAMS-model recipe.dag.gms written by dag2gams Converter at 29/03/2004 16:58:58
* University of Vienna
$offdigit;
 Set i/1*1/;
 Set j/1*3/;
 Equations objcon
con1
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= 0;


con1.. x('3') / ((- x('1')) + 
x('2')) =e= 0;
x.lo('1')=5;
x.up('1')=5;
x.lo('2')=-0;
x.up('2')=0;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


