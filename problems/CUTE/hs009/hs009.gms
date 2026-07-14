* GAMS-model hs009.dag.gms written by dag2gams Converter at 29/03/2004 16:53:53
* University of Vienna
$offdigit;
 Set i/1*1/;
 Set j/1*2/;
 Equations objcon
con1
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= cos(0.19634937499999999 * x('2')) * sin(0.26179916666666664 * x('1'));


con1.. 4 * x('1') - 
3 * x('2') =e= 0;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


