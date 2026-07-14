* GAMS-model hs027.dag.gms written by dag2gams Converter at 29/03/2004 16:58:58
* University of Vienna
$offdigit;
 Set i/1*1/;
 Set j/1*3/;
 Equations objcon
con1
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= 0.01 * power((x('2')) - 1, 2) + 
power(x('3') - 
power(x('2'), 2), 2);


con1.. x('2') + 
power(x('1'), 2) =e= -1;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


