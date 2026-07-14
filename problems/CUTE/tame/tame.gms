* GAMS-model tame.dag.gms written by dag2gams Converter at 29/03/2004 16:53:53
* University of Vienna
$offdigit;
 Set i/1*1/;
 Set j/1*2/;
 Equations objcon
con1
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= power(x('1') - 
x('2'), 2);


con1.. x('1') + 
x('2') =e= 1;
x.lo('1')=0;
x.lo('2')=0;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


