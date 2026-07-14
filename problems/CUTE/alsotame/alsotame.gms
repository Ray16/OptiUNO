* GAMS-model alsotame.dag.gms written by dag2gams Converter at 29/03/2004 16:53:53
* University of Vienna
$offdigit;
 Set i/1*1/;
 Set j/1*2/;
 Equations objcon
con1
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= exp(x('1') - 
2 * x('2'));


con1.. sin(-x('1') + 
x('2') - 
1) =e= 0;
x.lo('1')=-2;
x.up('1')=2;
x.lo('2')=-1.5;
x.up('2')=1.5;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


