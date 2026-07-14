* GAMS-model denschnc.dag.gms written by dag2gams Converter at 29/03/2004 16:53:53
* University of Vienna
$offdigit;
 Set j/1*2/;
 Equations objcon
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= power(exp(x('1') - 1) + 
power(x('2'), 3) - 
2, 2) + 
power(power(x('1'), 2) + 
power(x('2'), 2) - 
2, 2);


Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


