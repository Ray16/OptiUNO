* GAMS-model hs060.dag.gms written by dag2gams Converter at 29/03/2004 16:58:58
* University of Vienna
$offdigit;
 Set i/1*1/;
 Set j/1*3/;
 Equations objcon
con1
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= power((x('1')) - 1, 2) + 
power(x('1') - 
x('2'), 2) + 
power(x('2') - 
x('3'), 4);


con1.. x('1') * (power(x('2'), 2) + 
1) + 
power(x('3'), 4) =e= 8.2426406871192857;
x.lo('1')=-10;
x.up('1')=10;
x.lo('2')=-10;
x.up('2')=10;
x.lo('3')=-10;
x.up('3')=10;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


